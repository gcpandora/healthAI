from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ObjectiveEnum(str, Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    endurance = "endurance"
    flexibility = "flexibility"
    general_fitness = "general_fitness"


class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"


class RecommendationRequest(BaseModel):
    age: int = Field(..., ge=10, le=100)
    gender: GenderEnum
    weight_kg: float = Field(..., gt=0)
    height_m: float = Field(..., gt=0)
    experience_level: int = Field(..., ge=1, le=3, description="1=débutant, 2=intermédiaire, 3=avancé")
    objective: ObjectiveEnum
    equipment: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list, description="Ex: back_pain, knee_pain")


class ExerciseOut(BaseModel):
    name: str
    workout_type: str
    difficulty: int
    equipment: List[str]
    muscles_targeted: List[str]
    description: str
    duration_minutes: int
    calories_per_minute: float


class RecommendationResponse(BaseModel):
    recommended_workout_type: str
    confidence: float
    objective: str
    exercises: List[ExerciseOut]
    weekly_program: dict
    ml_scores: dict
