"""
Point d'entrée du service Publications & médias — VERSION MOCK.

Architecture en couches :
    Route → Controller → Repository → Model
Le main ne fait qu'ASSEMBLER : il monte les routers, configure CORS,
et expose quelques utilitaires de démo. Aucune logique ici.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import post, profile
from app.repository.memory import store

app = FastAPI(
    title="HealthAI Coach — API Publications",
    description=(
        "Service réseau social en architecture couches "
        "(routes / controllers / repositories / models). "
        "Stockage simulé en mémoire en attendant PostgreSQL."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Montage des routers
app.include_router(post.router)
app.include_router(profile.router)
app.include_router(profile.media_router)


# ─── Utilitaires démo / système ───
@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "mode": "mock"}


@app.post("/_reset", tags=["system"])
def reset_data():
    """Recharge le jeu de données initial (pratique pour démo et tests)."""
    store.reset()
    return {"status": "données réinitialisées"}
