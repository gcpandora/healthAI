from uuid import UUID
from sqlalchemy.orm import Session

from models.user_profile import UserProfile


class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def upsert(self, user_id: UUID, fields: dict) -> UserProfile:
        profile = self.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(
                user_id=user_id,
                display_name=fields.get("display_name", "Utilisateur"),
            )
            self.db.add(profile)
        for key, value in fields.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile
