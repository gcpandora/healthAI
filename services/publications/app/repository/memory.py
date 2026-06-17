"""
COUCHE REPOSITORY — Implémentation EN MÉMOIRE (mock).

C'est le SEUL fichier qui contient le stockage simulé.
Quand Hanane livre PostgreSQL, on crée un postgres.py qui implémente
les mêmes interfaces (base.py) avec SQLAlchemy, et on bascule dessus.

>>> EXEMPLE de ce que deviendra create() en version Postgres :
        def create(self, post):
            row = PostORM(**post.to_dict())
            self.session.add(row)
            self.session.commit()
            return post
    La signature ne change pas → le controller ne voit aucune différence.
"""
import copy
from app.models.Comment import Comment
from app.models.Like import Like
from app.models.Post import Post
from app.models.Profile import Profile
from app.repository import seed_data
from app.repository.base import (
    PostRepository, LikeRepository, CommentRepository, ProfileRepository,
)


# Stockage partagé en mémoire (simule les tables SQL)
class _Store:
    def __init__(self):
        self.reset()

    def reset(self):
        self.posts = {p["id"]: copy.deepcopy(p) for p in seed_data.POSTS}
        self.likes = copy.deepcopy(seed_data.LIKES)
        self.comments = {c["id"]: copy.deepcopy(c) for c in seed_data.COMMENTS}
        self.profiles = {p["user_id"]: copy.deepcopy(p) for p in seed_data.PROFILES}


store = _Store()


class MemoryPostRepository(PostRepository):
    def list(self, limit, cursor):
        ordered = sorted(store.posts.values(),
                         key=lambda p: p["created_at"], reverse=True)
        if cursor:
            ordered = [p for p in ordered if p["created_at"] < cursor]
        page = ordered[:limit]
        next_cursor = page[-1]["created_at"] if len(page) == limit else None
        return [Post(**p) for p in page], next_cursor

    def get(self, post_id):
        row = store.posts.get(post_id)
        return Post(**row) if row else None

    def create(self, post):
        store.posts[post.id] = post.to_dict()
        return post

    def delete(self, post_id):
        store.posts.pop(post_id, None)

    def count_likes(self, post_id):
        return sum(1 for l in store.likes if l["post_id"] == post_id)

    def count_comments(self, post_id):
        return sum(1 for c in store.comments.values() if c["post_id"] == post_id)


class MemoryLikeRepository(LikeRepository):
    def add(self, like):
        if not self.exists(like.post_id, like.user_id):
            store.likes.append(like.to_dict())

    def remove(self, post_id, user_id):
        before = len(store.likes)
        store.likes = [l for l in store.likes
                       if not (l["post_id"] == post_id and l["user_id"] == user_id)]
        return len(store.likes) < before

    def exists(self, post_id, user_id):
        return any(l["post_id"] == post_id and l["user_id"] == user_id
                   for l in store.likes)

    def remove_by_post(self, post_id):
        store.likes = [l for l in store.likes if l["post_id"] != post_id]


class MemoryCommentRepository(CommentRepository):
    def list(self, post_id, limit, cursor):
        items = [c for c in store.comments.values() if c["post_id"] == post_id]
        items = sorted(items, key=lambda c: c["created_at"])
        if cursor:
            items = [c for c in items if c["created_at"] > cursor]
        page = items[:limit]
        next_cursor = page[-1]["created_at"] if len(page) == limit else None
        return [Comment(**c) for c in page], next_cursor

    def add(self, comment):
        store.comments[comment.id] = comment.to_dict()
        return comment

    def remove_by_post(self, post_id):
        for cid in [c for c, v in store.comments.items() if v["post_id"] == post_id]:
            del store.comments[cid]


class MemoryProfileRepository(ProfileRepository):
    def get(self, user_id):
        row = store.profiles.get(user_id)
        return Profile(**row) if row else None

    def upsert(self, profile):
        store.profiles[profile.user_id] = profile.to_dict()
        return profile