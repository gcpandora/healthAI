from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_user_service
from core.database import get_db
from schemas.user import UserCreate, UserRead, UserUpdate
from services.user_service import UserService

router = APIRouter(prefix='/users', tags=['Users'])


@router.post('/', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.create_user(db, payload.model_dump())


@router.get('/', response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.list_users(db, skip=skip, limit=limit)


@router.get('/{user_id}', response_model=UserRead)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.get_user(db, user_id)


@router.put('/{user_id}', response_model=UserRead)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.update_user(db, user_id, payload.model_dump(exclude_unset=True))


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    service.delete_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
