from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_nutrition_item_service
from core.database import get_db
from schemas.nutrition import NutritionItemCreate, NutritionItemRead, NutritionItemUpdate
from services.nutrition_service import NutritionItemService

router = APIRouter(prefix='/nutrition-items', tags=['Nutrition Items'])


@router.post('/', response_model=NutritionItemRead, status_code=status.HTTP_201_CREATED)
def create_nutrition_item(payload: NutritionItemCreate, db: Session = Depends(get_db), service: NutritionItemService = Depends(get_nutrition_item_service)):
    return service.create_item(db, payload.model_dump())


@router.get('/', response_model=list[NutritionItemRead])
def list_nutrition_items(skip: int = 0, limit: int = 100, search: str | None = None, db: Session = Depends(get_db), service: NutritionItemService = Depends(get_nutrition_item_service)):
    return service.list_items(db, skip=skip, limit=limit, search=search)


@router.get('/{item_id}', response_model=NutritionItemRead)
def get_nutrition_item(item_id: UUID, db: Session = Depends(get_db), service: NutritionItemService = Depends(get_nutrition_item_service)):
    return service.get_item(db, item_id)


@router.put('/{item_id}', response_model=NutritionItemRead)
def update_nutrition_item(item_id: UUID, payload: NutritionItemUpdate, db: Session = Depends(get_db), service: NutritionItemService = Depends(get_nutrition_item_service)):
    return service.update_item(db, item_id, payload.model_dump(exclude_unset=True))


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_nutrition_item(item_id: UUID, db: Session = Depends(get_db), service: NutritionItemService = Depends(get_nutrition_item_service)):
    service.delete_item(db, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
