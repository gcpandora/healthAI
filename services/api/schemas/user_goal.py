from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from schemas.common import ORMBaseSchema


class UserGoalBase(ORMBaseSchema):
    user_id: UUID
    goal_type: Optional[Literal['weight_loss', 'muscle_gain', 'maintenance', 'sleep_improvement', 'general_health']] = None
    target_value: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class UserGoalCreate(UserGoalBase):
    pass


class UserGoalUpdate(ORMBaseSchema):
    goal_type: Optional[Literal['weight_loss', 'muscle_gain', 'maintenance', 'sleep_improvement', 'general_health']] = None
    target_value: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class UserGoalRead(UserGoalBase):
    id: UUID
    created_at: datetime
