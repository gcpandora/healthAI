import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from main import app

SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# scope="session" : créé une seule fois pour toute la suite de tests
# évite les violations de contrainte UNIQUE sur name/email/username
@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def created_user(client):
    payload = {
        "email": "fixture@healthai.com",
        "username": "fixture_user",
        "password": "secret123",
        "age": 30,
        "gender": "male",
    }
    r = client.post("/api/v1/users/", json=payload)
    assert r.status_code == 201
    return r.json()


@pytest.fixture(scope="session")
def created_exercise(client):
    payload = {"name": "Squat fixture", "difficulty": "beginner"}
    r = client.post("/api/v1/exercises/", json=payload)
    assert r.status_code == 201
    return r.json()


@pytest.fixture(scope="session")
def created_nutrition_item(client):
    payload = {"name": "Riz blanc fixture", "calories": 130, "proteins_g": 2.7}
    r = client.post("/api/v1/nutrition-items/", json=payload)
    assert r.status_code == 201
    return r.json()
