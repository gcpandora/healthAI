from sqlalchemy.orm import Session

from models.exercise import Exercise
from repositories.base import BaseRepository


class ExerciseRepository(BaseRepository[Exercise]):
    def __init__(self):
        super().__init__(Exercise)

    def search_by_name(self, db: Session, name: str, skip: int = 0, limit: int = 100):
        return (
            db.query(Exercise)
            .filter(Exercise.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )


exercise_repository = ExerciseRepository()
