import pytest


BASE = "/api/v1/nutrition-items"

ITEM_PAYLOAD = {
    "name": "Poulet rôti",
    "category": "viande",
    "calories": 165,
    "proteins_g": 31.0,
    "carbs_g": 0.0,
    "fats_g": 3.6,
}


def test_create_nutrition_item(client):
    r = client.post(f"{BASE}/", json=ITEM_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == ITEM_PAYLOAD["name"]
    assert float(data["calories"]) == 165.0
    assert "id" in data


def test_create_nutrition_item_missing_name(client):
    r = client.post(f"{BASE}/", json={"calories": 100})
    assert r.status_code == 422


def test_list_nutrition_items(client, created_nutrition_item):
    r = client.get(f"{BASE}/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_list_nutrition_items_search(client, created_nutrition_item):
    r = client.get(f"{BASE}/?search=Riz")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_nutrition_item(client, created_nutrition_item):
    item_id = created_nutrition_item["id"]
    r = client.get(f"{BASE}/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id


def test_get_nutrition_item_not_found(client):
    r = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_nutrition_item(client, created_nutrition_item):
    item_id = created_nutrition_item["id"]
    r = client.put(f"{BASE}/{item_id}", json={"calories": 150, "proteins_g": 3.0})
    assert r.status_code == 200
    assert float(r.json()["calories"]) == 150.0


def test_delete_nutrition_item(client):
    r = client.post(f"{BASE}/", json={"name": "Item à supprimer"})
    item_id = r.json()["id"]
    r = client.delete(f"{BASE}/{item_id}")
    assert r.status_code == 204
    assert client.get(f"{BASE}/{item_id}").status_code == 404


def test_delete_nutrition_item_not_found(client):
    r = client.delete(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
