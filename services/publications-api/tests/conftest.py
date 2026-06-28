"""
Configuration pytest pour les tests d'intégration de publications-api.
Utilise une base PostgreSQL réelle (DATABASE_URL en variable d'environnement).
"""

import os
import uuid
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql://test_user:test_password@localhost:5432/healthai_pub_test")
os.environ.setdefault("API_SECRET_KEY", "test_secret_key_for_ci")
os.environ.setdefault("MINIO_ENDPOINT", "")
os.environ.setdefault("MINIO_ACCESS_KEY", "")
os.environ.setdefault("MINIO_SECRET_KEY", "")

from core.config import settings  # noqa: E402 — env vars set above
from core.database import Base, engine as app_engine, SessionLocal  # noqa: E402
from main import app  # noqa: E402

TEST_DB_URL = settings.database_url
test_engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(bind=test_engine)


def _create_users_table(conn):
    conn.execute(text("""
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE TABLE IF NOT EXISTS users (
            id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email         VARCHAR(255) UNIQUE NOT NULL,
            username      VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            age           INTEGER,
            gender        VARCHAR(10),
            height_cm     NUMERIC(5,2),
            weight_kg     NUMERIC(5,2),
            water_intake_liters NUMERIC(4,2),
            created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """))


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    with test_engine.connect() as conn:
        conn.execute(text("COMMIT"))
        _create_users_table(conn)
        conn.commit()
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    with test_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()


@pytest.fixture(scope="function")
def db():
    session = TestSession()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="session")
def test_user_id() -> str:
    uid = str(uuid.uuid4())
    with test_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO users (id, email, username, password_hash)
            VALUES (:id, :email, :username, :pwd)
            ON CONFLICT (email) DO UPDATE SET username = EXCLUDED.username
        """), {"id": uid, "email": "integration@test.local",
               "username": "integration_user", "pwd": "hashed"})
        conn.commit()
    return uid


@pytest.fixture(scope="session")
def auth_token(test_user_id: str) -> str:
    payload = {
        "sub": test_user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
