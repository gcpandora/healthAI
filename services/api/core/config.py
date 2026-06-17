"""
HealthAI Coach — Configuration Centralisée
Chargement des variables d'environnement et configuration globale
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application HealthAI Coach."""
    
    # ─────────────────────────────────────────────────────────────────
    # Base de Données
    # ─────────────────────────────────────────────────────────────────
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://healthai_user:password@postgres:5432/healthai_db"
    )
    
    # ─────────────────────────────────────────────────────────────────
    # API Configuration
    # ─────────────────────────────────────────────────────────────────
    api_title: str = "HealthAI Coach API"
    api_description: str = "API REST pour la plateforme HealthAI Coach — MSPR TPRE501"
    api_version: str = "0.1.0"
    
    # Sécurité
    secret_key: str = os.getenv("API_SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    
    # Debug mode
    debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"

    # Micro-service IA
    ai_api_key: str = "dev_key"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://0.0.0.0:5173",
    ]
    
    # ─────────────────────────────────────────────────────────────────
    # Application
    # ─────────────────────────────────────────────────────────────────
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Récupère les settings (cached)."""
    return Settings()


# Export pour utilisation
settings = get_settings()
