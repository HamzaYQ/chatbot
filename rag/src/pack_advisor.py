"""
pack_advisor.py

Relie le moteur de scoring structuré (pricing_engine.py) et le LLM :
le calcul du classement des packs est 100% déterministe (pas de LLM),
le LLM intervient uniquement pour rédiger l'explication en langage naturel.
"""

import os
from typing import Any, Optional
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from src.pricing_engine import load_packs, load_eligibility, load_rules, recommend_packs

load_dotenv()


class PackAdvisor:
    def __init__(self, vector_store, embedding_manager, data_dir: str = "data/csv_data"):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

        self.packs = load_packs(f"{data_dir}/packs.csv")
        self.eligibility = load_eligibility(f"{data_dir}/pack_eligibility.csv")
        self.rules = load_rules(f"{data_dir}/pricing_rules.csv")

        self.llm = ChatGroq(
            groq_api_key=os.getenv('GROQ_API_KEY'),
            model='llama-3.3-70b-versatile',
            temperature=0.1,
            max_tokens=1024
        )

    def _get_pack_context(self, pack_name: str, top_k: int = 3) -> str:
        """Récupère du contexte narratif (MD/garanties) sur le pack recommandé, via RAG."""
        query = f"garanties et avantages du pack {pack_name} assurance auto"
        query_embedding = self.embedding_manager.embed_query(query)

        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            if results['documents'] and results['documents'][0]:
                return "\n\n".join(results['documents'][0])
        except Exception as e:
            print(f"[WARN] Échec de récupération du contexte pack: {e}")
        return ""

    def get_recommendation(self, profile: dict[str, Any], budget: Optional[float] = None, top_n: int = 4) -> dict:
        """
        Calcule le classement des packs (structuré) puis génère une explication (LLM).

        Returns:
            {
                "cards": [...],              # les top_n packs classés, prêts pour l'affichage
                "recommended_pack_id": str,  # le pack en tête
                "recommendation_text": str   # explication en langage naturel
            }
        """
        ranked = recommend_packs(profile, self.packs, self.eligibility, self.rules, budget=budget, top_n=top_n)

        if not ranked:
            return {
                "cards": [],
                "recommended_pack_id": None,
                "recommendation_text": "Aucun pack ne correspond à ce profil pour le moment."
            }

        top_pack = ranked[0]
        context = self._get_pack_context(top_pack['Nom'])

        packs_summary = "\n".join(
            f"- {p['Nom']} ({p['Segment']}): {p['EstimatedPrice']} MAD/an, "
            f"garanties: {', '.join(p['GarantiesIncluses']) if p['GarantiesIncluses'] else 'aucune'}"
            for p in ranked
        )

        prompt = f'''Tu es un conseiller assurance pour AssurAuto Maroc. Voici le profil du client
et les packs les mieux adaptés selon notre moteur de scoring interne (déjà calculé, ne recalcule rien).

Profil client: {profile}

Packs recommandés (classés du meilleur au moins bon):
{packs_summary}

Informations complémentaires sur le pack en tête ({top_pack['Nom']}):
{context if context else "Aucune information complémentaire disponible."}

Rédige une recommandation courte et personnalisée (5-6 phrases maximum) expliquant pourquoi le pack
{top_pack['Nom']} est le plus adapté à ce profil, en citant 2-3 critères concrets (budget, usage,
garanties). Reste factuel et ne mentionne jamais de calcul interne ou de score.'''

        response = self.llm.invoke(prompt)

        return {
            "cards": ranked,
            "recommended_pack_id": top_pack['PackID'],
            "recommendation_text": response.content
        }