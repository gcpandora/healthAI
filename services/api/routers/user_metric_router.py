from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_user_metric_service
from core.database import get_db
from schemas.user_metric import UserMetricCreate, UserMetricRead, UserMetricUpdate
from services.user_metric_service import UserMetricService

router = APIRouter(prefix='/user-metrics', tags=['User Metrics'])


@router.post('/', response_model=UserMetricRead, status_code=status.HTTP_201_CREATED)
def create_user_metric(payload: UserMetricCreate, db: Session = Depends(get_db), service: UserMetricService = Depends(get_user_metric_service)):
    return service.create_metric(db, payload.model_dump(exclude_unset=True))


@router.get('/', response_model=list[UserMetricRead])
def list_user_metrics(skip: int = 0, limit: int = 100, user_id: UUID | None = None, db: Session = Depends(get_db), service: UserMetricService = Depends(get_user_metric_service)):
    return service.list_metrics(db, skip=skip, limit=limit, user_id=user_id)


@router.get('/{metric_id}', response_model=UserMetricRead)
def get_user_metric(metric_id: UUID, db: Session = Depends(get_db), service: UserMetricService = Depends(get_user_metric_service)):
    return service.get_metric(db, metric_id)


@router.put('/{metric_id}', response_model=UserMetricRead)
def update_user_metric(metric_id: UUID, payload: UserMetricUpdate, db: Session = Depends(get_db), service: UserMetricService = Depends(get_user_metric_service)):
    return service.update_metric(db, metric_id, payload.model_dump(exclude_unset=True))


@router.delete('/{metric_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_user_metric(metric_id: UUID, db: Session = Depends(get_db), service: UserMetricService = Depends(get_user_metric_service)):
    service.delete_metric(db, metric_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
