from fastapi import APIRouter, Depends, Request
from app.middleware.auth import verify_api_key
from app.middleware.rate_limiter import limiter
from app.services import ai_service
from app.schemas.nutrition import MealPlanRequest, MealPlanResponse

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.post("/meal-plan", response_model=MealPlanResponse)
@limiter.limit("30/minute")
async def generate_meal_plan(
    request: Request,
    body: MealPlanRequest,
    _: str = Depends(verify_api_key),
):
    result = await ai_service.generate_meal_plan(
        objectif=body.objectif,
        calories_cible=body.calories_cible,
        duree_jours=body.duree_jours,
        budget=body.budget,
        regime=body.regime,
        allergies=body.allergies,
    )
    return result
