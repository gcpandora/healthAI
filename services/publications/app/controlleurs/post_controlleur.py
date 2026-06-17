"""
COUCHE CONTROLLER — Logique métier des publications.

Le controller :
- reçoit des données déjà validées (par les schémas)
- applique les RÈGLES MÉTIER (ex : un post doit avoir texte ou média)
- orchestre un ou plusieurs repositories
- ne connaît RIEN de HTTP (pas de status code, pas de Request FastAPI)
- ne connaît RIEN du stockage (il parle aux interfaces de repository)

Il reçoit ses repositories par injection (dans le constructeur) :
c'est ce qui permet de lui passer la version mémoire aujourd'hui
et la version PostgreSQL demain, sans rien changer ici.
"""
from app.models.Comment import Comment
from app.models.Like import Like
from app.models.Post import Post
from app.repository.base import (
    PostRepository, LikeRepository, CommentRepository,
)
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError


class PostController:
    def __init__(self, posts: PostRepository, likes: LikeRepository,
                 comments: CommentRepository, profiles):
        self.posts = posts
        self.likes = likes
        self.comments = comments
        self.profiles = profiles

    # ─── Posts ───
    def list_feed(self, limit: int, cursor: str | None) -> dict:
        items, next_cursor = self.posts.list(limit, cursor)
        return {"items": [self._to_out(p) for p in items], "next_cursor": next_cursor}

    def get_post(self, post_id: str) -> dict:
        post = self.posts.get(post_id)
        if not post:
            raise NotFoundError("Post introuvable")
        return self._to_out(post)

    def create_post(self, user_id: str, content: str, media_urls: list[str]) -> dict:
        # RÈGLE MÉTIER : un post vide est interdit
        if not content.strip() and not media_urls:
            raise ValidationError("Un post doit contenir du texte ou un média")
        post = Post(user_id=user_id, content=content, media_urls=media_urls)
        self.posts.create(post)
        return self._to_out(post)

    def delete_post(self, post_id: str, user_id: str) -> None:
        post = self.posts.get(post_id)
        if not post:
            raise NotFoundError("Post introuvable")
        # RÈGLE MÉTIER : seul l'auteur peut supprimer son post
        if post.user_id != user_id:
            raise ForbiddenError("Vous ne pouvez supprimer que vos propres posts")
        # Suppression en cascade (likes + commentaires)
        self.likes.remove_by_post(post_id)
        self.comments.remove_by_post(post_id)
        self.posts.delete(post_id)

    # ─── Likes ───
    def like(self, post_id: str, user_id: str) -> None:
        if not self.posts.get(post_id):
            raise NotFoundError("Post introuvable")
        self.likes.add(Like(post_id=post_id, user_id=user_id))

    def unlike(self, post_id: str, user_id: str) -> None:
        if not self.posts.get(post_id):
            raise NotFoundError("Post introuvable")
        self.likes.remove(post_id, user_id)

    # ─── Commentaires ───
    def list_comments(self, post_id: str, limit: int, cursor: str | None) -> dict:
        if not self.posts.get(post_id):
            raise NotFoundError("Post introuvable")
        items, next_cursor = self.comments.list(post_id, limit, cursor)
        return {"items": [c.to_dict() for c in items], "next_cursor": next_cursor}

    def add_comment(self, post_id: str, user_id: str, content: str) -> dict:
        if not self.posts.get(post_id):
            raise NotFoundError("Post introuvable")
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        self.comments.add(comment)
        return comment.to_dict()

    # ─── Helper : assemble un post enrichi (auteur + compteurs) ───
    def _to_out(self, post: Post) -> dict:
        author = self.profiles.get(post.user_id)
        return {
            **post.to_dict(),
            "author": {
                "user_id": post.user_id,
                "display_name": author.display_name if author else "Inconnu",
                "avatar_url": author.avatar_url if author else None,
            },
            "likes_count": self.posts.count_likes(post.id),
            "comments_count": self.posts.count_comments(post.id),
        }