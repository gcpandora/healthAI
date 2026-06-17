from sqlalchemy.orm import Session
from uuid import UUID

from repositories.food_log_repository import FoodLogRepository
from services.base import BaseService


class FoodLogService(BaseService):
    def __init__(self, repository: FoodLogRepository):
        super().__init__(repository)
        self.repository = repository

    def create_log(self, db: Session, data: dict):
        return self.repository.create(db, data)

    def list_logs(self, db: Session, skip: int = 0, limit: int = 100, user_id: UUID | None = None):
        if user_id:
            return self.repository.get_by_user(db, user_id, skip=skip, limit=limit)
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_log(self, db: Session, log_id: UUID):
        return self.get_or_404(db, log_id, 'Food log not found')

    def update_log(self, db: Session, log_id: UUID, data: dict):
        return self.update(db, log_id, data, 'Food log not found')

    def delete_log(self, db: Session, log_id: UUID) -> None:
        self.delete(db, log_id, 'Food log not found')
