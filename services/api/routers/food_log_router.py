from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_food_log_service
from core.database import get_db
from schemas.food_log import FoodLogCreate, FoodLogRead, FoodLogUpdate
from services.food_log_service import FoodLogService

router = APIRouter(prefix='/food-logs', tags=['Food Logs'])


@router.post('/', response_model=FoodLogRead, status_code=status.HTTP_201_CREATED)
def create_food_log(payload: FoodLogCreate, db: Session = Depends(get_db), service: FoodLogService = Depends(get_food_log_service)):
    return service.create_log(db, payload.model_dump())


@router.get('/', response_model=list[FoodLogRead])
def list_food_logs(skip: int = 0, limit: int = 100, user_id: UUID | None = None, db: Session = Depends(get_db), service: FoodLogService = Depends(get_food_log_service)):
    return service.list_logs(db, skip=skip, limit=limit, user_id=user_id)


@router.get('/{food_log_id}', response_model=FoodLogRead)
def get_food_log(food_log_id: UUID, db: Session = Depends(get_db), service: FoodLogService = Depends(get_food_log_service)):
    return service.get_log(db, food_log_id)


@router.put('/{food_log_id}', response_model=FoodLogRead)
def update_food_log(food_log_id: UUID, payload: FoodLogUpdate, db: Session = Depends(get_db), service: FoodLogService = Depends(get_food_log_service)):
    return service.update_log(db, food_log_id, payload.model_dump(exclude_unset=True))


@router.delete('/{food_log_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_food_log(food_log_id: UUID, db: Session = Depends(get_db), service: FoodLogService = Depends(get_food_log_service)):
    service.delete_log(db, food_log_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
