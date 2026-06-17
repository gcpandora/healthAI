from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from schemas.common import ORMBaseSchema


class WorkoutLogBase(ORMBaseSchema):
    user_id: UUID
    exercise_id: UUID
    duration_min: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    calories_burned: Optional[Decimal] = None


class WorkoutLogCreate(WorkoutLogBase):
    pass


class WorkoutLogUpdate(ORMBaseSchema):
    duration_min: Optional[int] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    calories_burned: Optional[Decimal] = None


class WorkoutLogRead(WorkoutLogBase):
    id: UUID
    logged_at: datetime
