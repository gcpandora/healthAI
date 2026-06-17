"""
COUCHE ROUTES — Endpoints publications / likes / commentaires.

Les routes sont MINCES : elles ne font que
  1. recevoir la requête (validation par les schémas)
  2. récupérer l'utilisateur courant
  3. déléguer au controller
  4. traduire les erreurs métier en codes HTTP
Aucune logique métier ni accès aux données ici.
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.Auth import current_user
from app.core.dependency import get_post_controller
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.controlleurs.post_controlleur import PostController
from app.schemas.schema import (
    PostCreate, CommentCreate, PostOut, PostPage, CommentPage,
)

router = APIRouter(tags=["posts"])


# ─── Posts ───
@router.get("/posts", response_model=PostPage)
def get_feed(limit: int = Query(10, ge=1, le=50), cursor: str | None = None,
             ctrl: PostController = Depends(get_post_controller)):
    """Flux paginé (cursor-based), du plus récent au plus ancien."""
    return ctrl.list_feed(limit, cursor)


@router.get("/posts/{post_id}", response_model=PostOut)
def read_post(post_id: str, ctrl: PostController = Depends(get_post_controller)):
    try:
        return ctrl.get_post(post_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.post("/posts", response_model=PostOut, status_code=201)
def create_post(payload: PostCreate,
                user: str = Depends(current_user),
                ctrl: PostController = Depends(get_post_controller)):
    try:
        return ctrl.create_post(user, payload.content, payload.media_urls)
    except ValidationError as e:
        raise HTTPException(400, str(e))


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: str,
                user: str = Depends(current_user),
                ctrl: PostController = Depends(get_post_controller)):
    try:
        ctrl.delete_post(post_id, user)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except ForbiddenError as e:
        raise HTTPException(403, str(e))


# ─── Likes ───
@router.post("/posts/{post_id}/like", status_code=204)
def like_post(post_id: str,
              user: str = Depends(current_user),
              ctrl: PostController = Depends(get_post_controller)):
    try:
        ctrl.like(post_id, user)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/posts/{post_id}/like", status_code=204)
def unlike_post(post_id: str,
                user: str = Depends(current_user),
                ctrl: PostController = Depends(get_post_controller)):
    try:
        ctrl.unlike(post_id, user)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


# ─── Commentaires ───
@router.get("/posts/{post_id}/comments", response_model=CommentPage)
def get_comments(post_id: str, limit: int = Query(20, ge=1, le=100),
                 cursor: str | None = None,
                 ctrl: PostController = Depends(get_post_controller)):
    try:
        return ctrl.list_comments(post_id, limit, cursor)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.post("/posts/{post_id}/comments", status_code=201)
def add_comment(post_id: str, payload: CommentCreate,
                user: str = Depends(current_user),
                ctrl: PostController = Depends(get_post_controller)):
    try:
        return ctrl.add_comment(post_id, user, payload.content)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
