from pydantic import BaseModel, Field
from typing import Literal


class DietPredictRequest(BaseModel):
    age:                     int   = Field(..., ge=18, le=100)
    gender:                  Literal["Male", "Female"]
    weight_kg:               float = Field(..., gt=0)
    height_cm:               float = Field(..., gt=0, description="Taille en centimètres")
    physical_activity_level: Literal["Active", "Moderate", "Sedentary"]
    weekly_exercise_hours:   float = Field(..., ge=0)
    daily_caloric_intake:    float = Field(..., gt=0)


class DietPredictResponse(BaseModel):
    diet_recommendation: str
    confidence:          float
    probabilities:       dict[str, float]
    source:              str


class FitnessLevelRequest(BaseModel):
    age:                    int   = Field(..., ge=18, le=100)
    gender:                 Literal["Male", "Female"]
    weight_kg:              float = Field(..., gt=0)
    height_m:               float = Field(..., gt=0, description="Taille en mètres")
    max_bpm:                int   = Field(..., gt=0)
    avg_bpm:                int   = Field(..., gt=0)
    resting_bpm:            int   = Field(..., gt=0)
    session_duration_hours: float = Field(..., gt=0)
    calories_burned:        float = Field(..., gt=0)
    fat_percentage:         float = Field(..., ge=0, le=100)
    water_intake_liters:    float = Field(..., gt=0)
    workout_frequency:      float = Field(..., ge=0, le=7, description="Séances par semaine")


class FitnessLevelResponse(BaseModel):
    experience_level: int
    label:            str
    confidence:       float
    probabilities:    dict[str, float]
    source:           str
