from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from schemas.common import ORMBaseSchema


class UserMetricBase(ORMBaseSchema):
    user_id: UUID
    weight_kg: Optional[Decimal] = None
    body_fat_pct: Optional[Decimal] = None
    bmi: Optional[Decimal] = None
    heart_rate_avg: Optional[int] = None
    heart_rate_max: Optional[int] = None
    heart_rate_rest: Optional[int] = None
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    calories_burned: Optional[Decimal] = None
    sleep_hours: Optional[Decimal] = None


class UserMetricCreate(UserMetricBase):
    recorded_at: Optional[datetime] = None


class UserMetricUpdate(ORMBaseSchema):
    recorded_at: Optional[datetime] = None
    weight_kg: Optional[Decimal] = None
    body_fat_pct: Optional[Decimal] = None
    bmi: Optional[Decimal] = None
    heart_rate_avg: Optional[int] = None
    heart_rate_max: Optional[int] = None
    heart_rate_rest: Optional[int] = None
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    calories_burned: Optional[Decimal] = None
    sleep_hours: Optional[Decimal] = None


class UserMetricRead(UserMetricBase):
    id: UUID
    recorded_at: datetime
