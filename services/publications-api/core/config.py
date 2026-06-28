import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://healthai_user:password@postgres:5432/healthai_db",
    )
    secret_key: str = os.getenv("API_SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    port: int = int(os.getenv("PORT", "8004"))

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
