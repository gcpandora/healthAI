from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from schemas.common import ORMBaseSchema


class FoodLogBase(ORMBaseSchema):
    user_id: UUID
    nutrition_item_id: UUID
    quantity_g: Decimal
    meal_type: Literal['breakfast', 'lunch', 'dinner', 'snack']


class FoodLogCreate(FoodLogBase):
    pass


class FoodLogUpdate(ORMBaseSchema):
    quantity_g: Decimal | None = None
    meal_type: Literal['breakfast', 'lunch', 'dinner', 'snack'] | None = None


class FoodLogRead(FoodLogBase):
    id: UUID
    logged_at: datetime
