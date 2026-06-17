from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from schemas.common import ORMBaseSchema


class NutritionItemBase(ORMBaseSchema):
    name: str
    category: Optional[str] = None
    meal_type: Optional[str] = None
    calories: Optional[Decimal] = None
    proteins_g: Optional[Decimal] = None
    carbs_g: Optional[Decimal] = None
    fats_g: Optional[Decimal] = None
    fiber_g: Optional[Decimal] = None
    sugar_g: Optional[Decimal] = None
    sodium_mg: Optional[Decimal] = None
    cholesterol_mg: Optional[Decimal] = None
    water_ml: Optional[Decimal] = None
    source: Optional[str] = None


class NutritionItemCreate(NutritionItemBase):
    pass


class NutritionItemUpdate(ORMBaseSchema):
    name: Optional[str] = None
    category: Optional[str] = None
    meal_type: Optional[str] = None
    calories: Optional[Decimal] = None
    proteins_g: Optional[Decimal] = None
    carbs_g: Optional[Decimal] = None
    fats_g: Optional[Decimal] = None
    fiber_g: Optional[Decimal] = None
    sugar_g: Optional[Decimal] = None
    sodium_mg: Optional[Decimal] = None
    cholesterol_mg: Optional[Decimal] = None
    water_ml: Optional[Decimal] = None
    source: Optional[str] = None


class NutritionItemRead(NutritionItemBase):
    id: UUID
    created_at: datetime
