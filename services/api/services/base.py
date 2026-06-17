from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from repositories.base import BaseRepository

ModelType = TypeVar('ModelType')


class BaseService(Generic[ModelType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    def create(self, db: Session, data: dict):
        return self.repository.create(db, data)

    def list(self, db: Session, skip: int = 0, limit: int = 100):
        return self.repository.get_all(db, skip=skip, limit=limit)

    def get_or_404(self, db: Session, obj_id: UUID, detail: str):
        obj = self.repository.get_by_id(db, obj_id)
        if not obj:
            raise HTTPException(status_code=404, detail=detail)
        return obj

    def update(self, db: Session, obj_id: UUID, data: dict, detail: str):
        db_obj = self.get_or_404(db, obj_id, detail)
        return self.repository.update(db, db_obj, data)

    def delete(self, db: Session, obj_id: UUID, detail: str) -> None:
        db_obj = self.get_or_404(db, obj_id, detail)
        self.repository.delete(db, db_obj)
