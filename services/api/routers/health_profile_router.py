from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_health_profile_service
from core.database import get_db
from schemas.health_profile import HealthProfileCreate, HealthProfileRead, HealthProfileUpdate
from services.health_profile_service import HealthProfileService

router = APIRouter(prefix='/health-profiles', tags=['Health Profiles'])


@router.post('/', response_model=HealthProfileRead, status_code=status.HTTP_201_CREATED)
def create_health_profile(payload: HealthProfileCreate, db: Session = Depends(get_db), service: HealthProfileService = Depends(get_health_profile_service)):
    return service.create_profile(db, payload.model_dump())


@router.get('/', response_model=list[HealthProfileRead])
def list_health_profiles(skip: int = 0, limit: int = 100, user_id: UUID | None = None, db: Session = Depends(get_db), service: HealthProfileService = Depends(get_health_profile_service)):
    return service.list_profiles(db, skip=skip, limit=limit, user_id=user_id)


@router.get('/{profile_id}', response_model=HealthProfileRead)
def get_health_profile(profile_id: UUID, db: Session = Depends(get_db), service: HealthProfileService = Depends(get_health_profile_service)):
    return service.get_profile(db, profile_id)


@router.put('/{profile_id}', response_model=HealthProfileRead)
def update_health_profile(profile_id: UUID, payload: HealthProfileUpdate, db: Session = Depends(get_db), service: HealthProfileService = Depends(get_health_profile_service)):
    return service.update_profile(db, profile_id, payload.model_dump(exclude_unset=True))


@router.delete('/{profile_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_health_profile(profile_id: UUID, db: Session = Depends(get_db), service: HealthProfileService = Depends(get_health_profile_service)):
    service.delete_profile(db, profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
