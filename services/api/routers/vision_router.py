import logging
import time
import uuid
from collections import defaultdict

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, UploadFile
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from models.meal_analysis import MealAnalysis
from schemas.meal_analysis import MealAnalysisResponse, NutritionSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vision", tags=["Vision IA"])

_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 10
RATE_WINDOW = 3600
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _check_rate_limit(ip: str) -> int:
    now = time.time()
    calls = _rate_store[ip]
    _rate_store[ip] = [t for t in calls if now - t < RATE_WINDOW]
    remaining = RATE_LIMIT - len(_rate_store[ip])
    if remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail=f"Limite de {RATE_LIMIT} analyses par heure atteinte. Réessayez plus tard.",
        )
    _rate_store[ip].append(now)
    return remaining - 1


def _build_balance(proteines: float, glucides: float, score_sante: float) -> str:
    if score_sante >= 7:
        return "balanced"
    if proteines < 20:
        return "protein_deficit"
    if glucides > 100:
        return "carb_excess"
    return "unknown"


def _build_response(result: dict, db_id: uuid.UUID) -> MealAnalysisResponse:
    aliments = result.get("aliments", [])
    detected_foods = [a["nom"] for a in aliments if "nom" in a]
    nutrition_data = result.get("nutrition", {})
    calories = float(nutrition_data.get("calories", 0))
    proteins = float(nutrition_data.get("proteines", 0))
    carbs = float(nutrition_data.get("glucides", 0))
    fats = float(nutrition_data.get("lipides", 0))
    source = result.get("source", "fallback_manual")
    score = float(result.get("score_sante", 5))
    balance = _build_balance(proteins, carbs, score)
    return MealAnalysisResponse(
        analysis_id=db_id,
        detected_foods=detected_foods,
        nutrition=NutritionSummary(
            calories=calories,
            proteins_g=proteins,
            carbs_g=carbs,
            fats_g=fats,
            is_estimated=source == "fallback",
        ),
        balance=balance,
        recommendations=result.get("conseils", []),
        confidence=score / 10,
        source=source,
        is_fallback=source == "fallback",
    )


def _save_analysis(db: Session, response: MealAnalysisResponse, image_filename: str) -> None:
    record = MealAnalysis(
        id=response.analysis_id,
        user_id=None,
        image_filename=image_filename,
        vision_source=response.source,
        detected_foods=response.detected_foods,
        calories_estimated=response.nutrition.calories,
        proteins_g=response.nutrition.proteins_g,
        carbs_g=response.nutrition.carbs_g,
        fats_g=response.nutrition.fats_g,
        nutritional_balance=response.balance,
        recommendations=response.recommendations,
        confidence_score=response.confidence,
        is_fallback=response.is_fallback,
    )
    db.add(record)
    db.commit()


@router.post("/analyze-meal", response_model=MealAnalysisResponse)
async def analyze_meal(
    request: Request,
    response: Response,
    file: UploadFile | None = None,
    description: str | None = Form(default=None),
    health_goal: str = Form(default="equilibre"),
    db: Session = Depends(get_db),
) -> MealAnalysisResponse:
    client_ip = request.client.host if request.client else "unknown"
    remaining = _check_rate_limit(client_ip)
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    logger.info("Analyse repas — IP=%s description=%s health_goal=%s has_file=%s",
                client_ip, description, health_goal, file is not None)

    analysis_id = uuid.uuid4()
    image_filename = ""
    file_content: bytes | None = None

    if file is not None:
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Fichier trop volumineux. Taille maximale : 5 MB.",
            )
        if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"Format non supporté : {file.content_type}. Formats acceptés : JPEG, PNG, WebP, GIF.",
            )
        image_filename = file.filename or "upload"

    try:
        form_data: dict = {"description": description or "", "health_goal": health_goal}
        files = None

        if file_content is not None:
            files = {"image": (image_filename, file_content, file.content_type or "image/jpeg")}

        async with httpx.AsyncClient(timeout=30.0) as client:
            ai_response = await client.post(
                "http://ai-api:8002/nutrition/analyze",
                data=form_data,
                files=files,
                headers={"X-API-Key": settings.ai_api_key},
            )
            ai_response.raise_for_status()
            result = ai_response.json()

        logger.info("Réponse ai-api reçue — source=%s", result.get("source"))
        meal_response = _build_response(result, analysis_id)
        _save_analysis(db, meal_response, image_filename)
        return meal_response

    except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
        logger.warning("Fallback activé — ai-api injoignable: %s", type(exc).__name__)
    except httpx.HTTPStatusError as exc:
        logger.warning("Fallback activé — ai-api HTTP %s", exc.response.status_code)
    except Exception as exc:
        logger.warning("Fallback activé — erreur inattendue: %s", exc)

    fallback_response = MealAnalysisResponse(
        analysis_id=analysis_id,
        detected_foods=["repas estimé (service IA indisponible)"],
        nutrition=NutritionSummary(
            calories=450, proteins_g=22, carbs_g=58, fats_g=14, is_estimated=True
        ),
        balance="balanced",
        recommendations=[
            "Service d'analyse IA temporairement indisponible.",
            "Les valeurs affichées sont des estimations génériques pour un repas équilibré moyen.",
            "Réessayez dans quelques instants pour une analyse précise de votre repas.",
        ],
        confidence=0.0,
        source="fallback_manual",
        is_fallback=True,
        message="Analyse IA indisponible — estimations génériques affichées.",
    )
    _save_analysis(db, fallback_response, image_filename)
    return fallback_response


@router.get("/analyze-meal/{analysis_id}", response_model=MealAnalysisResponse)
async def get_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db)) -> MealAnalysisResponse:
    record = db.query(MealAnalysis).filter(MealAnalysis.id == analysis_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Analyse introuvable")

    return MealAnalysisResponse(
        analysis_id=record.id,
        detected_foods=record.detected_foods or [],
        nutrition=NutritionSummary(
            calories=record.calories_estimated or 0,
            proteins_g=record.proteins_g or 0,
            carbs_g=record.carbs_g or 0,
            fats_g=record.fats_g or 0,
            is_estimated=record.is_fallback,
        ),
        balance=record.nutritional_balance,
        recommendations=record.recommendations or [],
        confidence=record.confidence_score,
        source=record.vision_source,
        is_fallback=record.is_fallback,
    )
