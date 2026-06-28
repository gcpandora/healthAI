from uuid import UUID
from sqlalchemy.orm import Session

from models.like import Like


class LikeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: UUID, user_id: UUID) -> Like | None:
        return (
            self.db.query(Like)
            .filter(Like.post_id == post_id, Like.user_id == user_id)
            .first()
        )

    def add(self, post_id: UUID, user_id: UUID) -> Like:
        like = Like(post_id=post_id, user_id=user_id)
        self.db.add(like)
        self.db.commit()
        return like

    def remove(self, like: Like) -> None:
        self.db.delete(like)
        self.db.commit()
