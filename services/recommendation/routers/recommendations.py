from fastapi import APIRouter
from models.schemas import RecommendationRequest, RecommendationResponse
from db.mongo import get_db
from ml.recommender import recommender

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    workout_type, confidence, ml_scores = recommender.recommend_workout_type(
        objective=request.objective.value,
        age=request.age,
        gender=request.gender.value,
        weight_kg=request.weight_kg,
        height_m=request.height_m,
        experience_level=request.experience_level,
    )

    try:
        db = get_db()
        cursor = db["exercises"].find({"workout_type": workout_type}, {"_id": 0})
        raw_exercises = await cursor.to_list(length=100)
    except Exception:
        raw_exercises = []

    filtered = recommender.filter_exercises(
        exercises=raw_exercises,
        limitations=request.limitations,
        equipment=request.equipment,
        experience_level=request.experience_level,
    )

    weekly_program = recommender.build_weekly_program(
        workout_type=workout_type,
        objective=request.objective.value,
        experience_level=request.experience_level,
    )

    return RecommendationResponse(
        recommended_workout_type=workout_type,
        confidence=confidence,
        objective=request.objective.value,
        exercises=filtered,
        weekly_program=weekly_program,
        ml_scores=ml_scores,
    )
