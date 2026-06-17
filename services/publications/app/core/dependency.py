"""
COUCHE DEPENDENCIES — Câblage de l'application (injection de dépendances).

C'EST LE FICHIER CLÉ DE L'ARCHITECTURE.
Ici on décide quelle implémentation de repository on utilise.

>>> POUR PASSER À POSTGRESQL <<<
1. Créer app/repositories/postgres.py (mêmes interfaces, code SQLAlchemy)
2. Remplacer les 4 lignes "Memory..." ci-dessous par les versions "Postgres..."
RIEN d'autre ne change : ni les controllers, ni les routes.
"""
from functools import lru_cache

from app.repository.memory import (
    MemoryPostRepository, MemoryLikeRepository,
    MemoryCommentRepository, MemoryProfileRepository,
)
from app.controlleurs.post_controlleur import PostController
from app.controlleurs.profil_controlleur import ProfileController


# ─── Choix de l'implémentation de stockage (LE point de bascule) ───
@lru_cache
def _repos():
    return {
        "posts": MemoryPostRepository(),
        "likes": MemoryLikeRepository(),
        "comments": MemoryCommentRepository(),
        "profiles": MemoryProfileRepository(),
    }
    # Version Postgres future :
    # return {
    #     "posts": PostgresPostRepository(session),
    #     "likes": PostgresLikeRepository(session),
    #     ...
    # }


# ─── Fournisseurs de controllers (injectés dans les routes via Depends) ───
def get_post_controller() -> PostController:
    r = _repos()
    return PostController(r["posts"], r["likes"], r["comments"], r["profiles"])


def get_profile_controller() -> ProfileController:
    r = _repos()
    return ProfileController(r["profiles"])