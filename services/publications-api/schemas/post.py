from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ─── Inputs ───
class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000, examples=["Ma séance du jour 💪"])
    media_urls: list[str] = Field(default_factory=list)


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500, examples=["Bravo !"])


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = None
    bio: str | None = None


# ─── Outputs ───
class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    display_name: str
    avatar_url: str | None = None


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    content: str
    media_urls: list[str]
    created_at: datetime
    updated_at: datetime
    author: AuthorOut | None = None
    likes_count: int = 0
    comments_count: int = 0


class PostPage(BaseModel):
    items: list[PostOut]
    next_cursor: str | None = None


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    post_id: UUID
    user_id: UUID
    content: str
    created_at: datetime


class CommentPage(BaseModel):
    items: list[CommentOut]
    next_cursor: str | None = None


class LikeToggleOut(BaseModel):
    liked: bool
    likes_count: int


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None
    created_at: datetime
    updated_at: datetime
