"""
HealthAI Coach — Micro-service Recommandations Sportives
Responsable : Houssem (ML) / Tom (DevOps)
Port : 8001
"""
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

import db.mongo as mongo_state
from routers.exercises import router as exercises_router
from routers.recommendations import router as recommendations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connexion MongoDB
    mongo_state.client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
    database = mongo_state.client[os.getenv("MONGO_DB", "healthai_exercises")]

    # Seed exercises si la collection est vide
    count = await database["exercises"].count_documents({})
    if count == 0:
        seed_path = os.path.join(os.path.dirname(__file__), "data", "exercises_seed.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            exercises = json.load(f)
        await database["exercises"].insert_many(exercises)
        print(f"[MongoDB] {len(exercises)} exercices chargés depuis le seed.")
    else:
        print(f"[MongoDB] {count} exercices déjà présents.")

    print("[ML] Modèle RandomForest prêt.")
    yield

    mongo_state.client.close()


app = FastAPI(
    title="HealthAI — Recommendation Engine",
    description="Micro-service de recommandations sportives multi-critères (RandomForest + règles expertes)",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercises_router)
app.include_router(recommendations_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "recommendation", "port": 8001}


@app.get("/metrics")
async def ml_metrics():
    from ml.recommender import recommender
    return {
        "model": "RandomForestClassifier",
        "training_samples": 973,
        "metrics": recommender.metrics,
    }
