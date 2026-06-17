from sqlalchemy.orm import Session
from uuid import UUID

from models.exercise import WorkoutLog
from repositories.base import BaseRepository


class WorkoutLogRepository(BaseRepository[WorkoutLog]):
    def __init__(self):
        super().__init__(WorkoutLog)

    def get_by_user(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
        return (
            db.query(WorkoutLog)
            .filter(WorkoutLog.user_id == user_id)
            .order_by(WorkoutLog.logged_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


workout_log_repository = WorkoutLogRepository()
