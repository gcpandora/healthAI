from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.post import Post
from models.comment import Comment
from repositories.post_repository import PostRepository
from repositories.like_repository import LikeRepository
from repositories.comment_repository import CommentRepository
from repositories.user_profile_repository import UserProfileRepository
from schemas.post import (
    PostCreate, PostOut, PostPage, AuthorOut,
    CommentCreate, CommentOut, CommentPage,
    LikeToggleOut, ProfileUpdate, ProfileOut,
)

router = APIRouter(tags=["posts"])
profile_router = APIRouter(tags=["profile"])


def _build_post_out(post: Post, repo: PostRepository) -> PostOut:
    author_row = repo.get_author(post.user_id)
    author = AuthorOut(
        user_id=post.user_id,
        display_name=author_row.display_name if author_row else "Inconnu",
        avatar_url=author_row.avatar_url if author_row else None,
    )
    return PostOut(
        id=post.id,
        user_id=post.user_id,
        content=post.content,
        media_urls=post.media_urls or [],
        created_at=post.created_at,
        updated_at=post.updated_at,
        author=author,
        likes_count=repo.count_likes(post.id),
        comments_count=repo.count_comments(post.id),
    )


# ─── GET /posts ───────────────────────────────────────────────────────────────
@router.get("/posts", response_model=PostPage)
def list_posts(
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(None),
    db: Session = Depends(get_db),
):
    repo = PostRepository(db)
    posts, next_cursor = repo.list(limit, cursor)
    return PostPage(
        items=[_build_post_out(p, repo) for p in posts],
        next_cursor=next_cursor,
    )


# ─── POST /posts ──────────────────────────────────────────────────────────────
@router.post("/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    repo = PostRepository(db)
    post = Post(
        user_id=UUID(user_id),
        content=payload.content,
        media_urls=payload.media_urls,
    )
    post = repo.create(post)
    return _build_post_out(post, repo)


# ─── GET /posts/{id} ──────────────────────────────────────────────────────────
@router.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: UUID, db: Session = Depends(get_db)):
    repo = PostRepository(db)
    post = repo.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post introuvable")
    return _build_post_out(post, repo)


# ─── DELETE /posts/{id} ───────────────────────────────────────────────────────
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    repo = PostRepository(db)
    post = repo.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post introuvable")
    if str(post.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres posts")
    repo.delete(post)


# ─── POST /posts/{id}/likes (toggle) ─────────────────────────────────────────
@router.post("/posts/{post_id}/likes", response_model=LikeToggleOut)
async def toggle_like(
    post_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    post_repo = PostRepository(db)
    like_repo = LikeRepository(db)
    if not post_repo.get(post_id):
        raise HTTPException(status_code=404, detail="Post introuvable")
    existing = like_repo.get(post_id, UUID(user_id))
    if existing:
        like_repo.remove(existing)
        liked = False
    else:
        like_repo.add(post_id, UUID(user_id))
        liked = True
    return LikeToggleOut(liked=liked, likes_count=post_repo.count_likes(post_id))


# ─── POST /posts/{id}/comments ────────────────────────────────────────────────
@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    post_id: UUID,
    payload: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    post_repo = PostRepository(db)
    comment_repo = CommentRepository(db)
    if not post_repo.get(post_id):
        raise HTTPException(status_code=404, detail="Post introuvable")
    comment = Comment(
        post_id=post_id,
        user_id=UUID(user_id),
        content=payload.content,
    )
    comment = comment_repo.create(comment)
    return CommentOut(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        content=comment.content,
        created_at=comment.created_at,
    )


# ─── GET /posts/{id}/comments ────────────────────────────────────────────────
@router.get("/posts/{post_id}/comments", response_model=CommentPage)
def list_comments(
    post_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(None),
    db: Session = Depends(get_db),
):
    post_repo = PostRepository(db)
    if not post_repo.get(post_id):
        raise HTTPException(status_code=404, detail="Post introuvable")
    comment_repo = CommentRepository(db)
    comments, next_cursor = comment_repo.list(post_id, limit, cursor)
    return CommentPage(
        items=[
            CommentOut(
                id=c.id,
                post_id=c.post_id,
                user_id=c.user_id,
                content=c.content,
                created_at=c.created_at,
            )
            for c in comments
        ],
        next_cursor=next_cursor,
    )


# ─── GET /users/me/profile ────────────────────────────────────────────────────
@profile_router.get("/users/me/profile", response_model=ProfileOut)
async def get_my_profile(
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    repo = UserProfileRepository(db)
    profile = repo.get_by_user_id(UUID(user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Profil introuvable")
    return ProfileOut(
        user_id=profile.user_id,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


# ─── PATCH /users/me/profile ──────────────────────────────────────────────────
@profile_router.patch("/users/me/profile", response_model=ProfileOut)
async def update_my_profile(
    payload: ProfileUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    repo = UserProfileRepository(db)
    profile = repo.upsert(UUID(user_id), payload.model_dump(exclude_none=True))
    return ProfileOut(
        user_id=profile.user_id,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
