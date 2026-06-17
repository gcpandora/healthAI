from sqlalchemy.orm import Session
from uuid import UUID

from repositories.nutrition_repository import NutritionItemRepository
from services.base import BaseService


class NutritionItemService(BaseService):
    def __init__(self, repository: NutritionItemRepository):
        super().__init__(repository)
        self.repository = repository

    def create_item(self, db: Session, data: dict):
        return self.repository.create(db, data)

    def list_items(self, db: Session, skip: int = 0, limit: int = 100, search: str | None = None):
        if search:
            return self.repository.search_by_name(db, search, skip=skip, limit=limit)
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_item(self, db: Session, item_id: UUID):
        return self.get_or_404(db, item_id, 'Nutrition item not found')

    def update_item(self, db: Session, item_id: UUID, data: dict):
        return self.update(db, item_id, data, 'Nutrition item not found')

    def delete_item(self, db: Session, item_id: UUID) -> None:
        self.delete(db, item_id, 'Nutrition item not found')
