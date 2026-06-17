from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_exercise_service
from core.database import get_db
from schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate
from services.exercise_service import ExerciseService

router = APIRouter(prefix='/exercises', tags=['Exercises'])


@router.post('/', response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def create_exercise(payload: ExerciseCreate, db: Session = Depends(get_db), service: ExerciseService = Depends(get_exercise_service)):
    return service.create_exercise(db, payload.model_dump())


@router.get('/', response_model=list[ExerciseRead])
def list_exercises(skip: int = 0, limit: int = 100, search: str | None = None, db: Session = Depends(get_db), service: ExerciseService = Depends(get_exercise_service)):
    return service.list_exercises(db, skip=skip, limit=limit, search=search)


@router.get('/{exercise_id}', response_model=ExerciseRead)
def get_exercise(exercise_id: UUID, db: Session = Depends(get_db), service: ExerciseService = Depends(get_exercise_service)):
    return service.get_exercise(db, exercise_id)


@router.put('/{exercise_id}', response_model=ExerciseRead)
def update_exercise(exercise_id: UUID, payload: ExerciseUpdate, db: Session = Depends(get_db), service: ExerciseService = Depends(get_exercise_service)):
    return service.update_exercise(db, exercise_id, payload.model_dump(exclude_unset=True))


@router.delete('/{exercise_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_exercise(exercise_id: UUID, db: Session = Depends(get_db), service: ExerciseService = Depends(get_exercise_service)):
    service.delete_exercise(db, exercise_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
