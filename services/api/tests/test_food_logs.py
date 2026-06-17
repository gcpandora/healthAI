import pytest


BASE = "/api/v1/food-logs"


def test_create_food_log(client, created_user, created_nutrition_item):
    payload = {
        "user_id": created_user["id"],
        "nutrition_item_id": created_nutrition_item["id"],
        "quantity_g": "150.00",
        "meal_type": "lunch",
    }
    r = client.post(f"{BASE}/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == created_user["id"]
    assert data["meal_type"] == "lunch"
    assert "id" in data


def test_create_food_log_invalid_meal_type(client, created_user, created_nutrition_item):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "nutrition_item_id": created_nutrition_item["id"],
        "quantity_g": "100",
        "meal_type": "gouter",
    })
    assert r.status_code == 422


def test_create_food_log_missing_required(client, created_user):
    r = client.post(f"{BASE}/", json={"user_id": created_user["id"]})
    assert r.status_code == 422


def test_list_food_logs(client, created_user, created_nutrition_item):
    client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "nutrition_item_id": created_nutrition_item["id"],
        "quantity_g": "100",
        "meal_type": "breakfast",
    })
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_food_logs_filter_by_user(client, created_user):
    r = client.get(f"{BASE}/?user_id={created_user['id']}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_food_log(client, created_user, created_nutrition_item):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "nutrition_item_id": created_nutrition_item["id"],
        "quantity_g": "200",
        "meal_type": "dinner",
    })
    log_id = r.json()["id"]
    r = client.get(f"{BASE}/{log_id}")
    assert r.status_code == 200
    assert r.json()["id"] == log_id


def test_get_food_log_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_food_log(client, created_user, created_nutrition_item):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "nutrition_item_id": created_nutrition_item["id"],
        "quantity_g": "100",
        "meal_type": "snack",
    })
    log_id = r.json()["id"]
    r = client.put(f"{BASE}/{log_id}", json={"quantity_g": "250", "meal_type": "lunch"})
    assert r.status_code == 200
    assert r.json()["meal_type"] == "lunch"


def test_delete_food_log(client, created_user, created_nutrition_item):
    r = client.post(f"{BASE}/", json={
        "user_id": created_user["id"],
        "nutrition_item_id": created_nutrition_item["id"],
        "quantity_g": "80",
        "meal_type": "breakfast",
    })
    log_id = r.json()["id"]
    r = client.delete(f"{BASE}/{log_id}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{log_id}").status_code == 404
