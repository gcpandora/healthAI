import pytest


BASE = "/api/v1/user-goals"


def test_create_user_goal(client, created_user):
    payload = {
        "user_id": created_user["id"],
        "goal_type": "weight_loss",
        "target_value": "70.00",
        "start_date": "2026-05-16",
        "end_date": "2026-08-16",
    }
    r = client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == created_user["id"]
    assert data["goal_type"] == "weight_loss"
    assert "id" in data


def test_create_user_goal_invalid_type(client, created_user):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "goal_type": "gain_happiness",
    })
    assert r.status_code == 422


def test_create_user_goal_missing_user_id(client):
    r = client.post(f"{BASE}/", json={"goal_type": "weight_loss"})
    assert r.status_code == 422


def test_list_user_goals(client, created_user):
    client.post(f"{BASE}/", json={"user_id": created_user["id"], "goal_type": "maintenance"})
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_user_goals_filter_by_user(client, created_user):
    r = client.get(f"{BASE}/?user_id={created_user['id']}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_goal(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "goal_type": "muscle_gain"})
    goal_id = r.json()["id"]
    r = client.get(f"{BASE}/{goal_id}")
    assert r.status_code == 200
    assert r.json()["id"] == goal_id


def test_get_user_goal_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_user_goal(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "goal_type": "endurance" if False else "general_health"})
    goal_id = r.json()["id"]
    r = client.put(f"{BASE}/{goal_id}", json={"goal_type": "sleep_improvement", "target_value": "8.00"})
    assert r.status_code == 200
    assert r.json()["goal_type"] == "sleep_improvement"


def test_delete_user_goal(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "goal_type": "maintenance"})
    goal_id = r.json()["id"]
    r = client.delete(f"{BASE}/{goal_id}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{goal_id}").status_code == 404
