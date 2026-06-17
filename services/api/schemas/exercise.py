from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from schemas.common import ORMBaseSchema


class ExerciseBase(ORMBaseSchema):
    name: str
    type: Optional[str] = None
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None
    difficulty: Literal['beginner', 'intermediate', 'advanced']
    instructions: Optional[str] = None
    external_id: Optional[str] = None
    source: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(ORMBaseSchema):
    name: Optional[str] = None
    type: Optional[str] = None
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None
    difficulty: Optional[Literal['beginner', 'intermediate', 'advanced']] = None
    instructions: Optional[str] = None
    external_id: Optional[str] = None
    source: Optional[str] = None


class ExerciseRead(ExerciseBase):
    id: UUID
    created_at: datetime
