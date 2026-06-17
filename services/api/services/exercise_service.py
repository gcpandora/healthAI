from sqlalchemy.orm import Session
from uuid import UUID

from repositories.exercise_repository import ExerciseRepository
from services.base import BaseService


class ExerciseService(BaseService):
    def __init__(self, repository: ExerciseRepository):
        super().__init__(repository)
        self.repository = repository

    def create_exercise(self, db: Session, data: dict):
        return self.repository.create(db, data)

    def list_exercises(self, db: Session, skip: int = 0, limit: int = 100, search: str | None = None):
        if search:
            return self.repository.search_by_name(db, search, skip=skip, limit=limit)
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_exercise(self, db: Session, exercise_id: UUID):
        return self.get_or_404(db, exercise_id, 'Exercise not found')

    def update_exercise(self, db: Session, exercise_id: UUID, data: dict):
        return self.update(db, exercise_id, data, 'Exercise not found')

    def delete_exercise(self, db: Session, exercise_id: UUID) -> None:
        self.delete(db, exercise_id, 'Exercise not found')
