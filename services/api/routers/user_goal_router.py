from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_user_goal_service
from core.database import get_db
from schemas.user_goal import UserGoalCreate, UserGoalRead, UserGoalUpdate
from services.user_goal_service import UserGoalService

router = APIRouter(prefix='/user-goals', tags=['User Goals'])


@router.post('/', response_model=UserGoalRead, status_code=status.HTTP_201_CREATED)
def create_user_goal(payload: UserGoalCreate, db: Session = Depends(get_db), service: UserGoalService = Depends(get_user_goal_service)):
    return service.create_goal(db, payload.model_dump())


@router.get('/', response_model=list[UserGoalRead])
def list_user_goals(skip: int = 0, limit: int = 100, user_id: UUID | None = None, db: Session = Depends(get_db), service: UserGoalService = Depends(get_user_goal_service)):
    return service.list_goals(db, skip=skip, limit=limit, user_id=user_id)


@router.get('/{goal_id}', response_model=UserGoalRead)
def get_user_goal(goal_id: UUID, db: Session = Depends(get_db), service: UserGoalService = Depends(get_user_goal_service)):
    return service.get_goal(db, goal_id)


@router.put('/{goal_id}', response_model=UserGoalRead)
def update_user_goal(goal_id: UUID, payload: UserGoalUpdate, db: Session = Depends(get_db), service: UserGoalService = Depends(get_user_goal_service)):
    return service.update_goal(db, goal_id, payload.model_dump(exclude_unset=True))


@router.delete('/{goal_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_user_goal(goal_id: UUID, db: Session = Depends(get_db), service: UserGoalService = Depends(get_user_goal_service)):
    service.delete_goal(db, goal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
