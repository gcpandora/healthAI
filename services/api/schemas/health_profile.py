from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from schemas.common import ORMBaseSchema


class HealthProfileBase(ORMBaseSchema):
    user_id: UUID
    disease_type: Optional[str] = None
    severity: Optional[Literal['mild', 'moderate', 'severe']] = None
    physical_activity_level: Optional[Literal['low', 'moderate', 'high']] = None
    cholesterol_mg_dl: Optional[Decimal] = None
    blood_pressure_mmhg: Optional[int] = None
    glucose_mg_dl: Optional[Decimal] = None
    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None
    preferred_cuisine: Optional[str] = None
    weekly_exercise_hours: Optional[Decimal] = None
    adherence_to_diet_plan: Optional[Decimal] = None
    dietary_nutrient_imbalance_score: Optional[Decimal] = None
    diet_recommendation: Optional[str] = None


class HealthProfileCreate(HealthProfileBase):
    pass


class HealthProfileUpdate(ORMBaseSchema):
    disease_type: Optional[str] = None
    severity: Optional[Literal['mild', 'moderate', 'severe']] = None
    physical_activity_level: Optional[Literal['low', 'moderate', 'high']] = None
    cholesterol_mg_dl: Optional[Decimal] = None
    blood_pressure_mmhg: Optional[int] = None
    glucose_mg_dl: Optional[Decimal] = None
    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None
    preferred_cuisine: Optional[str] = None
    weekly_exercise_hours: Optional[Decimal] = None
    adherence_to_diet_plan: Optional[Decimal] = None
    dietary_nutrient_imbalance_score: Optional[Decimal] = None
    diet_recommendation: Optional[str] = None


class HealthProfileRead(HealthProfileBase):
    id: UUID
    created_at: datetime
