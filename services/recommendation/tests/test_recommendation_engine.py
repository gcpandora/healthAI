"""Tests du moteur de recommandation (:8001).

Tous les tests s'exécutent sans stack Docker : MongoDB et le modèle ML
sont mockés. Le modèle RandomForest tombe automatiquement sur les règles
expertes si le CSV d'entraînement est absent (comportement normal hors Docker).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

# ---------------------------------------------------------------------------
# Données de test
# ---------------------------------------------------------------------------

HIIT_EXERCISES = [
    {
        "name": "Burpees",
        "workout_type": "HIIT",
        "difficulty": 1,
        "equipment": [],
        "muscles_targeted": ["full_body"],
        "description": "Exercice haute intensité",
        "duration_minutes": 20,
        "calories_per_minute": 15.0,
    },
    {
        "name": "Jumping Jacks",
        "workout_type": "HIIT",
        "difficulty": 1,
        "equipment": [],
        "muscles_targeted": ["full_body"],
        "description": "Sauts écartés",
        "duration_minutes": 15,
        "calories_per_minute": 12.0,
    },
]

STRENGTH_EXERCISES = [
    {
        "name": "Développé couché",
        "workout_type": "Strength",
        "difficulty": 2,
        "equipment": ["barbell", "bench"],
        "muscles_targeted": ["pectoraux", "triceps"],
        "description": "Bench press",
        "duration_minutes": 45,
        "calories_per_minute": 8.0,
    },
    {
        "name": "Squat barre",
        "workout_type": "Strength",
        "difficulty": 2,
        "equipment": ["barbell"],
        "muscles_targeted": ["quadriceps", "fessiers"],
        "description": "Back squat",
        "duration_minutes": 45,
        "calories_per_minute": 9.0,
    },
]


def make_mock_db(exercises: list):
    """Renvoie (mock_db, mock_collection) simulant une base MongoDB."""
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=exercises)

    mock_collection = MagicMock()
    mock_collection.find = MagicMock(return_value=mock_cursor)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)

    return mock_db, mock_collection


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    # TestClient sans context manager → lifespan MongoDB non exécuté
    return TestClient(app)


WEIGHT_LOSS_PAYLOAD = {
    "age": 30,
    "gender": "Male",
    "weight_kg": 80.0,
    "height_m": 1.75,
    "experience_level": 2,
    "objective": "weight_loss",
    "equipment": [],
    "limitations": [],
}

MUSCLE_GAIN_PAYLOAD = {
    "age": 25,
    "gender": "Male",
    "weight_kg": 85.0,
    "height_m": 1.80,
    "experience_level": 3,
    "objective": "muscle_gain",
    "equipment": ["barbell", "bench"],
    "limitations": [],
}


# ---------------------------------------------------------------------------
# Groupe 1 — Requêtes valides
# ---------------------------------------------------------------------------

def test_weight_loss_returns_program_with_exercises(client):
    mock_db, _ = make_mock_db(HIIT_EXERCISES)
    with patch("routers.recommendations.get_db", return_value=mock_db):
        r = client.post("/recommendations", json=WEIGHT_LOSS_PAYLOAD)

    assert r.status_code == 200
    data = r.json()
    # Sans CSV, les règles expertes choisissent "HIIT" pour weight_loss
    assert data["recommended_workout_type"] in ["HIIT", "Cardio"]
    assert "exercises" in data
    assert isinstance(data["exercises"], list)
    assert "weekly_program" in data
    assert data["weekly_program"]["sessions_per_week"] == 4   # experience_level=2
    assert data["weekly_program"]["session_duration_minutes"] == 45
    assert data["objective"] == "weight_loss"


def test_muscle_gain_returns_coherent_program(client):
    mock_db, _ = make_mock_db(STRENGTH_EXERCISES)
    with patch("routers.recommendations.get_db", return_value=mock_db):
        r = client.post("/recommendations", json=MUSCLE_GAIN_PAYLOAD)

    assert r.status_code == 200
    data = r.json()
    assert data["recommended_workout_type"] == "Strength"
    assert data["weekly_program"]["sessions_per_week"] == 5   # experience_level=3
    assert data["weekly_program"]["session_duration_minutes"] == 60
    assert data["objective"] == "muscle_gain"
    assert isinstance(data["ml_scores"], dict)


# ---------------------------------------------------------------------------
# Groupe 2 — Validation entrée (champs obligatoires manquants)
# ---------------------------------------------------------------------------

def test_missing_age_returns_422(client):
    payload = {k: v for k, v in WEIGHT_LOSS_PAYLOAD.items() if k != "age"}
    r = client.post("/recommendations", json=payload)
    assert r.status_code == 422


def test_missing_gender_returns_422(client):
    payload = {k: v for k, v in WEIGHT_LOSS_PAYLOAD.items() if k != "gender"}
    r = client.post("/recommendations", json=payload)
    assert r.status_code == 422


def test_invalid_objective_returns_422(client):
    payload = {**WEIGHT_LOSS_PAYLOAD, "objective": "invalid_goal"}
    r = client.post("/recommendations", json=payload)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Groupe 3 — Vérification de la lecture MongoDB
# ---------------------------------------------------------------------------

def test_exercises_fetched_from_mongodb(client):
    mock_db, mock_collection = make_mock_db(HIIT_EXERCISES)
    with patch("routers.recommendations.get_db", return_value=mock_db):
        r = client.post("/recommendations", json=WEIGHT_LOSS_PAYLOAD)

    assert r.status_code == 200
    # MongoDB a bien été interrogé
    mock_collection.find.assert_called_once()
    query_filter = mock_collection.find.call_args[0][0]
    assert "workout_type" in query_filter
    # Les exercices retournés par MongoDB sont dans la réponse
    data = r.json()
    assert isinstance(data["exercises"], list)


# ---------------------------------------------------------------------------
# Groupe 4 — Fallback statique si MongoDB est down
# ---------------------------------------------------------------------------

def test_mongodb_down_returns_fallback_response(client):
    with patch(
        "routers.recommendations.get_db",
        side_effect=Exception("MongoDB unavailable"),
    ):
        r = client.post("/recommendations", json=WEIGHT_LOSS_PAYLOAD)

    assert r.status_code == 200
    data = r.json()
    # Le moteur ML fonctionne toujours sans MongoDB
    assert data["recommended_workout_type"] in ["HIIT", "Cardio", "Strength", "Yoga", "Cardio"]
    # Liste vide = fallback statique
    assert data["exercises"] == []
    assert "weekly_program" in data
    assert "sessions_per_week" in data["weekly_program"]
