from fastapi import APIRouter, Depends

from app.middleware.auth import verify_api_key
from app.schemas.ml import (
    DietPredictRequest, DietPredictResponse,
    FitnessLevelRequest, FitnessLevelResponse,
)
from app.services import ml_service

router = APIRouter(prefix="/ml", tags=["ML Prédictif"])


@router.post(
    "/predict-diet",
    response_model=DietPredictResponse,
    summary="Recommandation diététique (Random Forest ml2)",
)
async def predict_diet(
    body: DietPredictRequest,
    _: str = Depends(verify_api_key),
):
    return ml_service.predict_diet(
        age=body.age,
        gender=body.gender,
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        physical_activity_level=body.physical_activity_level,
        weekly_exercise_hours=body.weekly_exercise_hours,
        daily_caloric_intake=body.daily_caloric_intake,
    )


@router.post(
    "/predict-fitness-level",
    response_model=FitnessLevelResponse,
    summary="Niveau d'expérience fitness (Random Forest ml2)",
)
async def predict_fitness_level(
    body: FitnessLevelRequest,
    _: str = Depends(verify_api_key),
):
    return ml_service.predict_fitness_level(
        age=body.age,
        gender=body.gender,
        weight_kg=body.weight_kg,
        height_m=body.height_m,
        max_bpm=body.max_bpm,
        avg_bpm=body.avg_bpm,
        resting_bpm=body.resting_bpm,
        session_duration_hours=body.session_duration_hours,
        calories_burned=body.calories_burned,
        fat_percentage=body.fat_percentage,
        water_intake_liters=body.water_intake_liters,
        workout_frequency=body.workout_frequency,
    )
