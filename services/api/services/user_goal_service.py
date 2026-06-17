from sqlalchemy.orm import Session
from uuid import UUID

from repositories.user_goal_repository import UserGoalRepository
from services.base import BaseService


class UserGoalService(BaseService):
    def __init__(self, repository: UserGoalRepository):
        super().__init__(repository)
        self.repository = repository

    def create_goal(self, db: Session, data: dict):
        return self.repository.create(db, data)

    def list_goals(self, db: Session, skip: int = 0, limit: int = 100, user_id: UUID | None = None):
        if user_id:
            return self.repository.get_by_user(db, user_id, skip=skip, limit=limit)
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_goal(self, db: Session, goal_id: UUID):
        return self.get_or_404(db, goal_id, 'User goal not found')

    def update_goal(self, db: Session, goal_id: UUID, data: dict):
        return self.update(db, goal_id, data, 'User goal not found')

    def delete_goal(self, db: Session, goal_id: UUID) -> None:
        self.delete(db, goal_id, 'User goal not found')
