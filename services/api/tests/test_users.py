import pytest


BASE = "/api/v1/users"

USER_PAYLOAD = {
    "email": "alice@test.com",
    "username": "alice",
    "password": "pass123",
    "age": 25,
    "gender": "female",
    "fitness_level": "beginner",
    "goal": "weight_loss",
    "plan": "free",
}


def test_create_user(client):
    r = client.post(f"{BASE}/", json=USER_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["username"] == USER_PAYLOAD["username"]
    assert "id" in data
    assert "password" not in data


def test_create_user_duplicate_email(client):
    client.post(f"{BASE}/", json=USER_PAYLOAD)
    r = client.post(f"{BASE}/", json=USER_PAYLOAD)
    assert r.status_code in (400, 409)


def test_create_user_missing_required_fields(client):
    r = client.post(f"{BASE}/", json={"email": "nousername@test.com"})
    assert r.status_code == 422


def test_list_users(client, created_user):
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_list_users_pagination(client):
    r = client.get(f"{BASE}/?skip=0&limit=2")
    assert r.status_code == 200
    assert len(r.json()) <= 2


def test_get_user(client, created_user):
    user_id = created_user["id"]
    r = client.get(f"{BASE}/{user_id}")
    assert r.status_code == 200
    assert r.json()["id"] == user_id


def test_get_user_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_user(client, created_user):
    user_id = created_user["id"]
    r = client.put(f"{BASE}/{user_id}", json={"age": 35, "fitness_level": "intermediate"})
    assert r.status_code == 200
    assert r.json()["age"] == 35
    assert r.json()["fitness_level"] == "intermediate"


def test_update_user_not_found(client):
    r = client.put(f"{BASE}/00000000-0000-0000-0000-000000000000", json={"age": 40})
    assert r.status_code == 404


def test_delete_user(client):
    payload = {**USER_PAYLOAD, "email": "todelete@test.com", "username": "todelete"}
    r = client.post(f"{BASE}/", json=payload)
    user_id = r.json()["id"]
    r = client.delete(f"{BASE}/{user_id}")
    assert r.status_code == 204
    r = client.get(f"{BASE}/{user_id}")
    assert r.status_code == 404


def test_delete_user_not_found(client):
    r = client.delete(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
