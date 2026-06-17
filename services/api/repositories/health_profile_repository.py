from sqlalchemy.orm import Session
from uuid import UUID

from models.health_profile import HealthProfile
from repositories.base import BaseRepository


class HealthProfileRepository(BaseRepository[HealthProfile]):
    def __init__(self):
        super().__init__(HealthProfile)

    def get_by_user(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
        return (
            db.query(HealthProfile)
            .filter(HealthProfile.user_id == user_id)
            .order_by(HealthProfile.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


health_profile_repository = HealthProfileRepository()
