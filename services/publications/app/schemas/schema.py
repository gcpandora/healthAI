"""
COUCHE SCHÉMAS — Validation et sérialisation (Pydantic v2).

Différence avec les Models :
- Models  = entités internes (ce qui circule DANS l'app)
- Schemas = contrats de l'API (ce qui ENTRE et SORT par HTTP)

FastAPI utilise ces schémas pour valider les requêtes ET générer
la doc Swagger automatiquement (ta tâche "Documentation OpenAPI").
"""
from pydantic import BaseModel, Field


# ─── Entrées ───
class PostCreate(BaseModel):
    content: str = Field(default="", max_length=2000, examples=["Ma séance du jour 💪"])
    media_urls: list[str] = Field(default_factory=list)


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000, examples=["Bravo !"])


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = None
    bio: str | None = Field(default=None, max_length=280)


# ─── Sorties ───
class AuthorOut(BaseModel):
    user_id: str
    display_name: str
    avatar_url: str | None = None


class PostOut(BaseModel):
    id: str
    user_id: str
    content: str
    media_urls: list[str]
    created_at: str
    updated_at: str
    author: AuthorOut
    likes_count: int
    comments_count: int


class PostPage(BaseModel):
    items: list[PostOut]
    next_cursor: str | None = None


class CommentOut(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: str


class CommentPage(BaseModel):
    items: list[CommentOut]
    next_cursor: str | None = None


class ProfileOut(BaseModel):
    user_id: str
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None
    created_at: str
    updated_at: str
