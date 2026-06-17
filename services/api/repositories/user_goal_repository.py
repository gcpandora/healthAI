from sqlalchemy.orm import Session
from uuid import UUID

from models.user_goal import UserGoal
from repositories.base import BaseRepository


class UserGoalRepository(BaseRepository[UserGoal]):
    def __init__(self):
        super().__init__(UserGoal)

    def get_by_user(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
        return (
            db.query(UserGoal)
            .filter(UserGoal.user_id == user_id)
            .order_by(UserGoal.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


user_goal_repository = UserGoalRepository()
