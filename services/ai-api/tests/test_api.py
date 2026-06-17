import pytest
from unittest.mock import AsyncMock, patch


MOCK_ANALYZE = {
    "aliments": [{"nom": "riz", "quantite": "200g", "calories": 260}],
    "nutrition": {"calories": 540, "proteines": 30.0, "glucides": 60.0, "lipides": 10.0},
    "score_sante": 8,
    "desequilibres": [],
    "conseils": ["Bon équilibre protéines/glucides."],
    "source": "ollama",
}

MOCK_MEAL_PLAN = {
    "plan": [
        {
            "jour": 1,
            "petit_dejeuner": {"nom": "Porridge", "calories": 350, "ingredients": ["avoine", "lait"]},
            "dejeuner": {"nom": "Salade poulet", "calories": 600, "ingredients": ["poulet", "salade"]},
            "diner": {"nom": "Saumon légumes", "calories": 550, "ingredients": ["saumon", "brocolis"]},
            "total_calories": 1500,
        }
    ],
    "source": "ollama",
}

MOCK_ACTIVITY = {
    "programme": [
        {
            "jour": 1,
            "type_seance": "Cardio",
            "exercices": [{"nom": "Course", "series": 1, "repetitions": "30 min", "repos_sec": 0}],
            "duree_estimee_min": 30,
        }
    ],
    "conseils": ["Hydratez-vous bien."],
    "source": "ollama",
}


def test_health_no_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "services" in data


def test_analyze_without_auth(client):
    r = client.post("/nutrition/analyze", data={"description": "riz saumon"})
    assert r.status_code == 401


@patch("app.services.ai_service.analyze_nutrition", new_callable=AsyncMock, return_value=MOCK_ANALYZE)
def test_analyze_with_auth(mock_fn, client, auth_headers):
    r = client.post(
        "/nutrition/analyze",
        data={"description": "riz saumon brocolis", "health_goal": "equilibre"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert "aliments" in data
    assert "score_sante" in data
    assert data["source"] == "ollama"


@patch("app.services.ai_service.generate_meal_plan", new_callable=AsyncMock, return_value=MOCK_MEAL_PLAN)
def test_meal_plan(mock_fn, client, auth_headers):
    r = client.post(
        "/nutrition/meal-plan",
        json={"objectif": "perte_poids", "calories_cible": 1800, "duree_jours": 1},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert "plan" in data
    assert len(data["plan"]) == 1


@patch("app.services.ai_service.recommend_activity", new_callable=AsyncMock, return_value=MOCK_ACTIVITY)
def test_activity_recommend(mock_fn, client, auth_headers):
    r = client.post(
        "/activity/recommend",
        json={"objectif": "perte_poids", "niveau": "debutant", "duree_seance_min": 30},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert "programme" in data


def test_analyze_fallback(client, auth_headers):
    with patch("app.services.ai_service.analyze_nutrition", new_callable=AsyncMock) as mock_fn:
        mock_fn.return_value = {
            "aliments": [{"nom": "Repas non identifié", "quantite": "1 portion", "calories": 500}],
            "nutrition": {"calories": 500, "proteines": 25.0, "glucides": 60.0, "lipides": 15.0},
            "score_sante": 5,
            "desequilibres": ["Analyse IA indisponible — données estimées"],
            "conseils": ["Consultez un nutritionniste."],
            "source": "fallback",
        }
        r = client.post(
            "/nutrition/analyze",
            data={"description": "test"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["source"] == "fallback"
