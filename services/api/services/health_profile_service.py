from sqlalchemy.orm import Session
from uuid import UUID

from repositories.health_profile_repository import HealthProfileRepository
from services.base import BaseService


class HealthProfileService(BaseService):
    def __init__(self, repository: HealthProfileRepository):
        super().__init__(repository)
        self.repository = repository

    def create_profile(self, db: Session, data: dict):
        return self.repository.create(db, data)

    def list_profiles(self, db: Session, skip: int = 0, limit: int = 100, user_id: UUID | None = None):
        if user_id:
            return self.repository.get_by_user(db, user_id, skip=skip, limit=limit)
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_profile(self, db: Session, profile_id: UUID):
        return self.get_or_404(db, profile_id, 'Health profile not found')

    def update_profile(self, db: Session, profile_id: UUID, data: dict):
        return self.update(db, profile_id, data, 'Health profile not found')

    def delete_profile(self, db: Session, profile_id: UUID) -> None:
        self.delete(db, profile_id, 'Health profile not found')
