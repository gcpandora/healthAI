from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NutritionSummary(BaseModel):
    calories: float
    proteins_g: float
    carbs_g: float
    fats_g: float
    is_estimated: bool


class MealAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: UUID
    detected_foods: list[str]
    nutrition: NutritionSummary
    balance: str
    recommendations: list[str]
    confidence: float
    source: str  # "huggingface" | "google_vision" | "fallback_manual"
    is_fallback: bool
    message: Optional[str] = None
