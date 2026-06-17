import pytest


BASE = "/api/v1/exercises"

EXERCISE_PAYLOAD = {
    "name": "Développé couché",
    "type": "strength",
    "muscle_group": "chest",
    "equipment": "barbell",
    "difficulty": "intermediate",
    "instructions": "Allongé sur le banc, poussez la barre vers le haut.",
}


def test_create_exercise(client):
    r = client.post(f"{BASE}/", json=EXERCISE_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == EXERCISE_PAYLOAD["name"]
    assert data["difficulty"] == "intermediate"
    assert "id" in data


def test_create_exercise_missing_difficulty(client):
    r = client.post(f"{BASE}/", json={"name": "Curl"})
    assert r.status_code == 422


def test_create_exercise_invalid_difficulty(client):
    r = client.post(f"{BASE}/", json={"name": "Curl2", "difficulty": "expert"})
    assert r.status_code == 422


def test_list_exercises(client, created_exercise):
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_list_exercises_with_search(client, created_exercise):
    r = client.get(f"{BASE}/?search=Squat")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_exercise(client, created_exercise):
    exercise_id = created_exercise["id"]
    r = client.get(f"{BASE}/{exercise_id}")
    assert r.status_code == 200
    assert r.json()["id"] == exercise_id


def test_get_exercise_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_exercise(client, created_exercise):
    exercise_id = created_exercise["id"]
    r = client.put(f"{BASE}/{exercise_id}", json={"difficulty": "advanced", "muscle_group": "legs"})
    assert r.status_code == 200
    assert r.json()["difficulty"] == "advanced"
    assert r.json()["muscle_group"] == "legs"


def test_delete_exercise(client):
    r = client.post(f"{BASE}/", json={"name": "Exo à supprimer", "difficulty": "beginner"})
    exercise_id = r.json()["id"]
    r = client.delete(f"{BASE}/{exercise_id}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{exercise_id}").status_code == 404


def test_delete_exercise_not_found(client):
    r = client.delete(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
