from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, post_id: UUID, limit: int, cursor: str | None) -> tuple[list[Comment], str | None]:
        q = (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
        )
        if cursor:
            try:
                ts = datetime.fromisoformat(cursor)
                q = q.filter(Comment.created_at > ts)
            except ValueError:
                pass
        rows = q.limit(limit + 1).all()
        has_more = len(rows) > limit
        page = rows[:limit]
        next_cursor = page[-1].created_at.isoformat() if has_more else None
        return page, next_cursor

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
