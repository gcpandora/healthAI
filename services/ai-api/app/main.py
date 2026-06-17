from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.middleware.rate_limiter import limiter
from app.routes import nutrition, meal_plan, activity, health, ml

app = FastAPI(
    title="HealthAI Coach — API IA",
    description="API de recommandations personnalisées en nutrition et activité physique.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nutrition.router)
app.include_router(meal_plan.router)
app.include_router(activity.router)
app.include_router(health.router)
app.include_router(ml.router)


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "HealthAI Coach API IA — v1.0.0", "docs": "/docs"}
