from src.embedding import EmbeddingPipeline
from src.vector_store import VectorStore
from typing import Any
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
import os
from dotenv import load_dotenv
load_dotenv()

class RAGRetriever:
    '''Handles query based retrieavl from the vector store'''
    MAX_HISTORY_TURNS = 5
    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingPipeline):
        '''
        Initialize the retriever

        Args:
            vector_store: Vector store containing document embeddings
            embedding_manager: Manager for generating query embeddings
        '''
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.llm = ChatGroq(groq_api_key=self.groq_api_key, model='llama-3.3-70b-versatile', temperature=0.1, max_tokens=2048)
        self.llm_reform = ChatMistralAI(api_key=self.mistral_api_key, model="mistral-small-latest", temperature=0)
        # Mémoire de la conversation en cours, pas de persistance disque
        self.conversation_history: list[dict[str, str]] = []

    def _add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        # Garde uniquement les N derniers échanges (N tours = 2*N messages)
        max_messages = self.MAX_HISTORY_TURNS * 2
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]

    def _format_history(self) -> str:
        if not self.conversation_history:
            return ""
        lines = []
        for msg in self.conversation_history:
            speaker = "Client" if msg["role"] == "user" else "Assistant"
            lines.append(f"{speaker}: {msg['content']}")
        return "\n".join(lines)
    
    def _reformulate_query(self, query: str) -> str:
        '''
        Reformule la question courante en requête autonome, en s'appuyant sur
        l'historique, pour que le retrieval reste pertinent sur des questions
        elliptiques (ex: "et le prix ?" après une question sur un sujet précis).
        '''
        if not self.conversation_history:
            return query  # premier tour, rien à reformuler

        history_text = self._format_history()
        reformulation_prompt = f'''Voici l'historique d'une conversation entre un client et un assistant d'assurance auto.
            En te basant sur cet historique, reformule la dernière question du client en une question autonome et complète,
            compréhensible sans le reste de la conversation. Ne réponds pas à la question, reformule-la seulement.
            Si la question est déjà autonome, renvoie-la telle quelle.

            Historique:
            {history_text}

            Dernière question du client: {query}

            Question reformulée:'''

        try:
            result = self.llm_reform.invoke(reformulation_prompt)
            reformulated = result.content.strip()
            print(f'[INFO] Requête reformulée: "{query}" -> "{reformulated}"')
            return reformulated if reformulated else query
        except Exception as e:
            print(f'[WARN] Échec de la reformulation, utilisation de la requête originale: {e}')
            return query
    
    def retrieve(self, query: str, top_k: int = 3, score_threshold: float = 0.0) -> list[dict[str, Any]]:
        '''
        Retrieve relevant documents for a query

        Args:
            query: The search query
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold

        Returns: 
            List of dictionnaries containing retrieved documents and metadata
        '''
        print(f'Retrieving documents for query: "{query}"')
        print(f'Top K : {top_k}, Score threshold: {score_threshold}')

        # Generate query embedding
        query_embedding = self.embedding_manager.embed_query(query)

        # Search in vector store
        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )

            # Process results
            retrieved_docs = []

            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]

                for i, (doc_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances)):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1 - distance
                    
                    if similarity_score >= score_threshold:
                        retrieved_docs.append({
                            'id': doc_id,
                            'content': document,
                            'metadata': metadata,
                            'similarity_score': similarity_score,
                            'distance': distance,
                            'rank': i + 1
                        })
                print(f'Retrieved {len(retrieved_docs)} documents (after filtering)')
            else:
                print('No documents found')
            
            return retrieved_docs
    
        except Exception as e:
            print(f'Error during retrieval: {e}')
            return []
        
    def response(self, query):
        # 1. Reformule la question en s'appuyant sur l'historique (retrieval plus pertinent)
        search_query = self._reformulate_query(query)
        # 2. Récupère le contexte pertinent
        results = self.retrieve(search_query)
        context = "\n\n".join([doc['content'] for doc in results]) if results else ""
        if not context:
            answer = "Je n'ai pas trouvé d'information pertinente pour répondre à cette question."
            self._add_to_history("user", query)
            self._add_to_history("assistant", answer)
            return answer
         # 3. Construit le prompt avec historique + contexte
        history_text = self._format_history()
        history_block = f"\nHistorique de la conversation:\n{history_text}\n" if history_text else ""
        
        ## Generate the answer using GROQ LLM 
        prompt = f'''Tu es un assistant pour AssurAuto Maroc. Utilise le contexte suivant pour répondre
            à la question du client de façon concise. Si l'historique de conversation est fourni, tiens-en compte
            pour comprendre le fil de la discussion.
            {history_block}
            Contexte:
            {context}

            Question actuelle du client: {query}

            Réponse:'''
        
        response = self.llm.invoke(prompt)
        answer = response.content

        # 4. Met à jour la mémoire avec la question ORIGINALE (pas reformulée) et la réponse
        self._add_to_history("user", query)
        self._add_to_history("assistant", answer)

        return answer
    
    def reset_memory(self):
        '''Réinitialise la mémoire conversationnelle (nouvelle session client).'''
        self.conversation_history = []