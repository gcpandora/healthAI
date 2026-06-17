from sqlalchemy.orm import Session

from models.nutrition import NutritionItem
from repositories.base import BaseRepository


class NutritionItemRepository(BaseRepository[NutritionItem]):
    def __init__(self):
        super().__init__(NutritionItem)

    def search_by_name(self, db: Session, name: str, skip: int = 0, limit: int = 100):
        return (
            db.query(NutritionItem)
            .filter(NutritionItem.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )


nutrition_item_repository = NutritionItemRepository()
