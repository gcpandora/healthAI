"""
COUCHE REPOSITORY — Les interfaces (contrats).

On définit ICI ce qu'un repository DOIT savoir faire, sans dire COMMENT.
- Aujourd'hui : implémentation en mémoire (memory.py)
- Demain : implémentation PostgreSQL (postgres.py) qui respecte le MÊME contrat

Le controller dépend de l'interface, jamais de l'implémentation.
=> Pour passer à PostgreSQL, on écrit une nouvelle classe ici et on
   change UNE ligne dans le fichier de dépendances. Rien d'autre ne bouge.
"""
from abc import ABC, abstractmethod
from app.models.Comment import Comment
from app.models.Like import Like
from app.models.Post import Post
from app.models.Profile import Profile


class PostRepository(ABC):
    @abstractmethod
    def list(self, limit: int, cursor: str | None) -> tuple[list[Post], str | None]: ...

    @abstractmethod
    def get(self, post_id: str) -> Post | None: ...

    @abstractmethod
    def create(self, post: Post) -> Post: ...

    @abstractmethod
    def delete(self, post_id: str) -> None: ...

    @abstractmethod
    def count_likes(self, post_id: str) -> int: ...

    @abstractmethod
    def count_comments(self, post_id: str) -> int: ...


class LikeRepository(ABC):
    @abstractmethod
    def add(self, like: Like) -> None: ...

    @abstractmethod
    def remove(self, post_id: str, user_id: str) -> bool: ...

    @abstractmethod
    def exists(self, post_id: str, user_id: str) -> bool: ...

    @abstractmethod
    def remove_by_post(self, post_id: str) -> None: ...


class CommentRepository(ABC):
    @abstractmethod
    def list(self, post_id: str, limit: int, cursor: str | None) -> tuple[list[Comment], str | None]: ...

    @abstractmethod
    def add(self, comment: Comment) -> Comment: ...

    @abstractmethod
    def remove_by_post(self, post_id: str) -> None: ...


class ProfileRepository(ABC):
    @abstractmethod
    def get(self, user_id: str) -> Profile | None: ...

    @abstractmethod
    def upsert(self, profile: Profile) -> Profile: ...