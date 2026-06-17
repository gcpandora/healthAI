import pytest


BASE = "/api/v1/health-profiles"


def test_create_health_profile(client, created_user):
    payload = {
        "user_id": created_user["id"],
        "disease_type": "diabetes",
        "severity": "mild",
        "physical_activity_level": "moderate",
        "cholesterol_mg_dl": 190.0,
        "blood_pressure_mmhg": 120.0,
        "glucose_mg_dl": 95.0,
        "dietary_restrictions": "low_sugar",
        "weekly_exercise_hours": 3.5,
    }
    r = client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == created_user["id"]
    assert data["disease_type"] == "diabetes"
    assert "id" in data


def test_create_health_profile_missing_user_id(client):
    r = client.post(f"{BASE}/", json={"severity": "mild"})
    assert r.status_code == 422


def test_create_health_profile_invalid_severity(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "severity": "critical"})
    assert r.status_code == 422


def test_list_health_profiles(client, created_user):
    client.post(f"{BASE}/", json={"user_id": created_user["id"]})
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_health_profiles_filter_by_user(client, created_user):
    r = client.get(f"{BASE}/?user_id={created_user['id']}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_health_profile(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"], "severity": "moderate"})
    profile_id = r.json()["id"]
    r = client.get(f"{BASE}/{profile_id}")
    assert r.status_code == 200
    assert r.json()["id"] == profile_id


def test_get_health_profile_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_health_profile(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"]})
    profile_id = r.json()["id"]
    r = client.put(f"{BASE}/{profile_id}", json={"severity": "severe", "glucose_mg_dl": 110.0})
    assert r.status_code == 200
    assert r.json()["severity"] == "severe"


def test_delete_health_profile(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"]})
    profile_id = r.json()["id"]
    r = client.delete(f"{BASE}/{profile_id}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{profile_id}").status_code == 404
