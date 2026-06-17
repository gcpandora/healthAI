from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_workout_log_service
from core.database import get_db
from schemas.workout_log import WorkoutLogCreate, WorkoutLogRead, WorkoutLogUpdate
from services.workout_log_service import WorkoutLogService

router = APIRouter(prefix='/workout-logs', tags=['Workout Logs'])


@router.post('/', response_model=WorkoutLogRead, status_code=status.HTTP_201_CREATED)
def create_workout_log(payload: WorkoutLogCreate, db: Session = Depends(get_db), service: WorkoutLogService = Depends(get_workout_log_service)):
    return service.create_log(db, payload.model_dump())


@router.get('/', response_model=list[WorkoutLogRead])
def list_workout_logs(skip: int = 0, limit: int = 100, user_id: UUID | None = None, db: Session = Depends(get_db), service: WorkoutLogService = Depends(get_workout_log_service)):
    return service.list_logs(db, skip=skip, limit=limit, user_id=user_id)


@router.get('/{workout_log_id}', response_model=WorkoutLogRead)
def get_workout_log(workout_log_id: UUID, db: Session = Depends(get_db), service: WorkoutLogService = Depends(get_workout_log_service)):
    return service.get_log(db, workout_log_id)


@router.put('/{workout_log_id}', response_model=WorkoutLogRead)
def update_workout_log(workout_log_id: UUID, payload: WorkoutLogUpdate, db: Session = Depends(get_db), service: WorkoutLogService = Depends(get_workout_log_service)):
    return service.update_log(db, workout_log_id, payload.model_dump(exclude_unset=True))


@router.delete('/{workout_log_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_workout_log(workout_log_id: UUID, db: Session = Depends(get_db), service: WorkoutLogService = Depends(get_workout_log_service)):
    service.delete_log(db, workout_log_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
