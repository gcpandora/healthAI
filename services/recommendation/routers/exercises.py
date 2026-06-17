from fastapi import APIRouter, Query
from db.mongo import get_db

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("")
async def list_exercises(
    workout_type: str = Query(None, description="Filtrer par type: Cardio, Strength, HIIT, Yoga"),
    difficulty: int = Query(None, ge=1, le=3),
):
    db = get_db()
    query = {}
    if workout_type:
        query["workout_type"] = workout_type
    if difficulty:
        query["difficulty"] = difficulty

    cursor = db["exercises"].find(query, {"_id": 0})
    exercises = await cursor.to_list(length=200)
    return {"count": len(exercises), "exercises": exercises}
