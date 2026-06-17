from sqlalchemy.orm import Session
from uuid import UUID

from models.user_metric import UserMetric
from repositories.base import BaseRepository


class UserMetricRepository(BaseRepository[UserMetric]):
    def __init__(self):
        super().__init__(UserMetric)

    def get_by_user(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
        return (
            db.query(UserMetric)
            .filter(UserMetric.user_id == user_id)
            .order_by(UserMetric.recorded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


user_metric_repository = UserMetricRepository()
