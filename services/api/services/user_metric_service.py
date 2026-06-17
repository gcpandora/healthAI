from sqlalchemy.orm import Session
from uuid import UUID

from repositories.user_metric_repository import UserMetricRepository
from services.base import BaseService


class UserMetricService(BaseService):
    def __init__(self, repository: UserMetricRepository):
        super().__init__(repository)
        self.repository = repository

    def create_metric(self, db: Session, data: dict):
        return self.repository.create(db, data)

    def list_metrics(self, db: Session, skip: int = 0, limit: int = 100, user_id: UUID | None = None):
        if user_id:
            return self.repository.get_by_user(db, user_id, skip=skip, limit=limit)
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_metric(self, db: Session, metric_id: UUID):
        return self.get_or_404(db, metric_id, 'User metric not found')

    def update_metric(self, db: Session, metric_id: UUID, data: dict):
        return self.update(db, metric_id, data, 'User metric not found')

    def delete_metric(self, db: Session, metric_id: UUID) -> None:
        self.delete(db, metric_id, 'User metric not found')
