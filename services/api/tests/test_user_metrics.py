import pytest


BASE = "/api/v1/user-metrics"


def test_create_user_metric(client, created_user):
    payload = {
        "user_id": created_user["id"],
        "weight_kg": 75.5,
        "body_fat_pct": 18.0,
        "bmi": 23.1,
        "heart_rate_avg": 68,
        "steps": 8500,
        "calories_burned": 420.0,
        "sleep_hours": 7.5,
    }
    r = client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == created_user["id"]
    assert float(data["weight_kg"]) == 75.5
    assert "id" in data


def test_create_user_metric_missing_user_id(client):
    r = client.post(f"{BASE}/", json={"weight_kg": 70.0})
    assert r.status_code == 422


def test_list_user_metrics(client, created_user):
    client.post(f"{BASE}/", json={"user_id": created_user["id"], "weight_kg": 70.0})
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_user_metrics_filter_by_user(client, created_user):
    r = client.get(f"{BASE}/?user_id={created_user['id']}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_metric(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "steps": 10000})
    metric_id = r.json()["id"]
    r = client.get(f"{BASE}/{metric_id}")
    assert r.status_code == 200
    assert r.json()["id"] == metric_id


def test_get_user_metric_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_user_metric(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "weight_kg": 80.0})
    metric_id = r.json()["id"]
    r = client.put(f"{BASE}/{metric_id}", json={"weight_kg": 78.5, "sleep_hours": 8.0})
    assert r.status_code == 200
    assert float(r.json()["weight_kg"]) == 78.5
    assert float(r.json()["sleep_hours"]) == 8.0


def test_delete_user_metric(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "heart_rate_avg": 72})
    metric_id = r.json()["id"]
    r = client.delete(f"{BASE}/{metric_id}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{metric_id}").status_code == 404
