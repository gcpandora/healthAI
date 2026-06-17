"""
COUCHE ROUTES — Profil utilisateur + upload média (stub).
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.Auth import current_user
from app.core.dependency import get_profile_controller
from app.core.exceptions import NotFoundError
from app.controlleurs.profil_controlleur import ProfileController
from app.schemas.schema import ProfileUpdate, ProfileOut

router = APIRouter(tags=["profile"])


@router.get("/users/me/profile", response_model=ProfileOut)
def my_profile(user: str = Depends(current_user),
               ctrl: ProfileController = Depends(get_profile_controller)):
    try:
        return ctrl.get_my_profile(user)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.patch("/users/me/profile", response_model=ProfileOut)
def update_my_profile(payload: ProfileUpdate,
                      user: str = Depends(current_user),
                      ctrl: ProfileController = Depends(get_profile_controller)):
    return ctrl.update_my_profile(user, payload.model_dump(exclude_unset=True))


# ─── Upload média : STUB en attendant MinIO ───
media_router = APIRouter(tags=["media"])


@media_router.post("/media/upload")
def upload_media_stub():
    """
    PLACEHOLDER. Le vrai upload MinIO viendra avec ta tâche dédiée.
    Renvoie une fausse URL signée pour qu'Hélie code son écran de post.
    """
    return {
        "url": "http://localhost:9000/healthai-media/posts/mock-upload.jpg",
        "note": "STUB — MinIO pas encore branché",
    }
