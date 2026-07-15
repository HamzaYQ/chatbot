from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.manifest import ProcessingManifest
from src.data_loader import discover_files, load_csv_documents, load_md_documents
from src.embedding import EmbeddingPipeline
from src.vector_store import VectorStore
from src.retrieving import RAGRetriever
from src.pack_advisor import PackAdvisor

app = FastAPI()

# Autoriser Angular (localhost:4200) à appeler cette API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialisation UNIQUE au démarrage du serveur ---
chunker = EmbeddingPipeline()
chromadb_store = VectorStore()
pack_advisor = PackAdvisor(chromadb_store, chunker, data_dir="data/csv_data")

# Mémoire conversationnelle PAR SESSION (pas globale) — chaque client Angular
# a son propre historique, identifié par un session_id généré côté frontend.
sessions: dict[str, RAGRetriever] = {}


def get_or_create_session(session_id: str) -> RAGRetriever:
    if session_id not in sessions:
        sessions[session_id] = RAGRetriever(chromadb_store, chunker)
    return sessions[session_id]


# --- Schémas ---

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str

class WelcomeOption(BaseModel):
    id: str
    label: str

class WelcomeResponse(BaseModel):
    message: str
    options: list[WelcomeOption]

class ClientProfile(BaseModel):
    Age: Optional[float] = None
    Ville: Optional[str] = None
    Profession: Optional[str] = None
    Usage: Optional[str] = None
    Kilometrage: Optional[float] = None
    GarageFerme: Optional[str] = None
    Marque: Optional[str] = None
    Categorie: Optional[str] = None
    Carburant: Optional[str] = None
    BonusMalus: Optional[float] = None
    NombreSinistres5Ans: Optional[float] = None
    AncienneteClient: Optional[float] = None
    PuissanceCV: Optional[float] = None
    budget: Optional[float] = None


# --- Endpoints ---

@app.get("/welcome", response_model=WelcomeResponse)
def welcome():
    return WelcomeResponse(
        message="Bonjour et bienvenue chez AssurAuto Maroc ! Je suis votre assistant virtuel. Comment puis-je vous aider ?",
        options=[
            WelcomeOption(id="choisir_pack", label="Choisir un pack adapté à mon profil"),
        ]
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    retriever = get_or_create_session(request.session_id)
    answer = retriever.response(request.query)
    return ChatResponse(answer=answer)


@app.post("/recommend-packs")
def recommend_packs_endpoint(profile: ClientProfile):
    profile_dict = profile.dict(exclude={"budget"}, exclude_none=True)
    try:
        result = pack_advisor.get_recommendation(profile_dict, budget=profile.budget, top_n=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul de la recommandation: {e}")
    return result