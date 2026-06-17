from fastapi import APIRouter, Depends, Request
from app.middleware.auth import verify_api_key
from app.middleware.rate_limiter import limiter
from app.services import ai_service
from app.schemas.activity import ActivityRecommendRequest, ActivityRecommendResponse

router = APIRouter(prefix="/activity", tags=["Activité"])


@router.post("/recommend", response_model=ActivityRecommendResponse)
@limiter.limit("30/minute")
async def recommend_activity(
    request: Request,
    body: ActivityRecommendRequest,
    _: str = Depends(verify_api_key),
):
    result = await ai_service.recommend_activity(
        objectif=body.objectif,
        niveau=body.niveau,
        duree_seance_min=body.duree_seance_min,
        equipements=body.equipements,
        limitations=body.limitations,
    )
    return result
