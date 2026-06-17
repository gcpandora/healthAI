from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from pydantic import EmailStr

from schemas.common import ORMBaseSchema


class UserBase(ORMBaseSchema):
    email: str
    username: str
    age: Optional[int] = None
    gender: Optional[Literal['male', 'female', 'other']] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    water_intake_liters: Optional[Decimal] = None
    workout_frequency: Optional[int] = None
    fitness_level: Optional[Literal['beginner', 'intermediate', 'advanced']] = 'beginner'
    goal: Literal['weight_loss', 'muscle_gain', 'sleep_improvement', 'maintenance', 'general_health'] = 'general_health'
    plan: Literal['free', 'premium', 'premium_plus'] = 'free'
    role: Literal['user', 'admin'] = 'user'


class UserCreate(UserBase):
    password: str


class UserUpdate(ORMBaseSchema):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal['male', 'female', 'other']] = None
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    water_intake_liters: Optional[Decimal] = None
    workout_frequency: Optional[int] = None
    fitness_level: Optional[Literal['beginner', 'intermediate', 'advanced']] = None
    goal: Optional[Literal['weight_loss', 'muscle_gain', 'sleep_improvement', 'maintenance', 'general_health']] = None
    plan: Optional[Literal['free', 'premium', 'premium_plus']] = None
    role: Optional[Literal['user', 'admin']] = None


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
