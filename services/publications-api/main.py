from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import engine, Base
import models.post          # noqa: F401 — enregistre les tables dans Base.metadata
import models.comment       # noqa: F401
import models.like          # noqa: F401
import models.user_profile  # noqa: F401

from routers.health import router as health_router
from routers.media import router as media_router
from routers.posts import router as posts_router, profile_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HealthAI Coach — API Publications",
    description="Service réseau social : publications, likes, commentaires, profils.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(posts_router)
app.include_router(profile_router)
app.include_router(media_router)
