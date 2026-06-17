from sqlalchemy.orm import Session
from uuid import UUID

from models.food_logs import FoodLog
from repositories.base import BaseRepository


class FoodLogRepository(BaseRepository[FoodLog]):
    def __init__(self):
        super().__init__(FoodLog)

    def get_by_user(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
        return (
            db.query(FoodLog)
            .filter(FoodLog.user_id == user_id)
            .order_by(FoodLog.logged_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


food_log_repository = FoodLogRepository()
