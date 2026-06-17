from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from app.middleware.auth import verify_api_key
from app.middleware.rate_limiter import limiter
from app.services import ai_service
from app.schemas.nutrition import NutritionAnalyzeResponse
from fastapi import Request

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.post("/analyze", response_model=NutritionAnalyzeResponse)
@limiter.limit("30/minute")
async def analyze_meal(
    request: Request,
    description: Optional[str] = Form(None),
    health_goal: str = Form("equilibre"),
    image: Optional[UploadFile] = File(None),
    _: str = Depends(verify_api_key),
):
    image_bytes = await image.read() if image else None
    result = await ai_service.analyze_nutrition(
        description=description or "",
        health_goal=health_goal,
        image_bytes=image_bytes,
    )
    return result
