from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.post import Post
from models.like import Like
from models.comment import Comment
from models.user_profile import UserProfile


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, limit: int, cursor: str | None) -> tuple[list[Post], str | None]:
        q = self.db.query(Post).order_by(Post.created_at.desc())
        if cursor:
            try:
                ts = datetime.fromisoformat(cursor)
                q = q.filter(Post.created_at < ts)
            except ValueError:
                pass
        rows = q.limit(limit + 1).all()
        has_more = len(rows) > limit
        page = rows[:limit]
        next_cursor = page[-1].created_at.isoformat() if has_more else None
        return page, next_cursor

    def get(self, post_id: UUID) -> Post | None:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def create(self, post: Post) -> Post:
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        self.db.delete(post)
        self.db.commit()

    def count_likes(self, post_id: UUID) -> int:
        return self.db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar() or 0

    def count_comments(self, post_id: UUID) -> int:
        return self.db.query(func.count(Comment.id)).filter(Comment.post_id == post_id).scalar() or 0

    def get_author(self, user_id: UUID) -> UserProfile | None:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
