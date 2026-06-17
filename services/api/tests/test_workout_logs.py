import pytest


BASE = "/api/v1/workout-logs"


def test_create_workout_log(client, created_user, created_exercise):
    payload = {
        "user_id": created_user["id"],
        "exercise_id": created_exercise["id"],
        "duration_min": 45,
        "sets": 4,
        "reps": 12,
        "calories_burned": 300.0,
    }
    r = client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == created_user["id"]
    assert data["duration_min"] == 45
    assert "id" in data


def test_create_workout_log_missing_required(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"]})
    assert r.status_code == 422


def test_create_workout_log_invalid_duration(client, created_user, created_exercise):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "exercise_id": created_exercise["id"],
        "duration_min": "pas_un_nombre",
    })
    assert r.status_code == 422


def test_list_workout_logs(client, created_user, created_exercise):
    client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "exercise_id": created_exercise["id"],
        "duration_min": 30,
    })
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_workout_logs_filter_by_user(client, created_user):
    r = client.get(f"{BASE}/?user_id={created_user['id']}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_workout_log(client, created_user, created_exercise):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "exercise_id": created_exercise["id"],
        "duration_min": 60,
    })
    log_id = r.json()["id"]
    r = client.get(f"{BASE}/{log_id}")
    assert r.status_code == 200
    assert r.json()["id"] == log_id


def test_get_workout_log_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_workout_log(client, created_user, created_exercise):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "exercise_id": created_exercise["id"],
        "duration_min": 20,
    })
    log_id = r.json()["id"]
    r = client.put(f"{BASE}/{log_id}", json={"duration_min": 35, "sets": 3, "reps": 10})
    assert r.status_code == 200
    assert r.json()["duration_min"] == 35
    assert r.json()["sets"] == 3


def test_delete_workout_log(client, created_user, created_exercise):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "exercise_id": created_exercise["id"],
        "duration_min": 25,
    })
    log_id = r.json()["id"]
    r = client.delete(f"{BASE}/{log_id}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{log_id}").status_code == 404
