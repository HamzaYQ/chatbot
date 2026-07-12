from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

class EmbeddingPipeline:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model = SentenceTransformer(model_name)
        print(f"[INFO] Loaded embedding model: {model_name}")

        self.md_header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("##", "section")],
            strip_headers=False
        )
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def _chunk_md_documents(self, documents: List[Any]) -> List[Any]:
        """Chunk MD documents by section (##), puis re-split si une section dépasse chunk_size."""
        all_chunks = []
        for doc in tqdm(documents, desc="Chunking MD"):
            sections = self.md_header_splitter.split_text(doc.page_content)
            for section in sections:
                section.metadata = {**doc.metadata, **section.metadata}

            sub_chunks = self.recursive_splitter.split_documents(sections)

            # chunk_index remis à zéro pour CHAQUE document source, pas global
            for idx, chunk in enumerate(sub_chunks):
                chunk.metadata["chunk_index"] = idx

            all_chunks.extend(sub_chunks)

        print(f"[INFO] Split {len(documents)} MD documents into {len(all_chunks)} chunks.")
        return all_chunks

    def _chunk_csv_documents(self, documents: List[Any]) -> List[Any]:
        """
        CSVLoader produit déjà 1 doc = 1 ligne. On ne chunk que si une ligne
        dépasse chunk_size, pour éviter de casser la structure colonne:valeur.
        """
        chunks = []
        for doc in tqdm(documents, desc="Chunking CSV"):
            if len(doc.page_content) <= self.chunk_size:
                sub_chunks = [doc]
            else:
                sub_chunks = self.recursive_splitter.split_documents([doc])

            # chunk_index remis à zéro pour CHAQUE ligne CSV source
            for idx, chunk in enumerate(sub_chunks):
                chunk.metadata["chunk_index"] = idx

            chunks.extend(sub_chunks)

        print(f"[INFO] Processed {len(documents)} CSV documents into {len(chunks)} chunks.")
        return chunks

    def chunk_documents(self, documents: List[Any], doc_type: str = "generic") -> List[Any]:
        """
        Chunk according to document type.

        Args:
            documents: documents list
            doc_type: documents type -> 'md', 'csv', generic(default type)
        """
        if doc_type == "md":
            chunks = self._chunk_md_documents(documents)
        elif doc_type == "csv":
            chunks = self._chunk_csv_documents(documents)
        else:
            chunks = self.recursive_splitter.split_documents(documents)
            for idx, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = idx
            print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks.")

        return chunks

    def embed_chunks(self, chunks: List[Any], batch_size: int = 4, normalize: bool = True) -> np.ndarray:
        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=normalize,
        )
        print(f"[INFO] Embeddings shape: {embeddings.shape}")
        return embeddings
    
    def embed_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """Utilisé au moment de la recherche, pas de l'indexation — prompt différent."""
        return self.model.encode(
            query,
            normalize_embeddings=normalize,
        )
    
# if __name__ == '__main__':
#     docs = load_md_documents('./test')
#     chunker = EmbeddingPipeline()
#     md_chunks = chunker._chunk_md_documents(docs)
#     embedded_chunks = chunker.embed_chunks(md_chunks)
#     prompt = 'Bienvenue dans le test!'
#     while prompt != 'n':
#         index = int(input("Saisir l'indice :"))
#         print(md_chunks[index])
#         print(embedded_chunks[index])
#         prompt = input("Refaire le test ? y/n")
