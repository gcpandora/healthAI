import pytest
from tests.conftest import TEST_USER_ID


@pytest.fixture(scope="module")
def created_post(client):
    r = client.post("/posts", json={"content": "Hello HealthAI!", "media_urls": []})
    assert r.status_code == 201
    return r.json()


def test_create_post(client):
    r = client.post("/posts", json={"content": "Test publication", "media_urls": []})
    assert r.status_code == 201
    data = r.json()
    assert data["content"] == "Test publication"
    assert data["user_id"] == TEST_USER_ID
    assert data["media_urls"] == []
    assert "id" in data


def test_create_post_with_media(client):
    r = client.post(
        "/posts",
        json={"content": "Post avec média", "media_urls": ["http://minio/img.jpg"]},
    )
    assert r.status_code == 201
    assert r.json()["media_urls"] == ["http://minio/img.jpg"]


def test_create_post_too_long(client):
    r = client.post("/posts", json={"content": "x" * 2001, "media_urls": []})
    assert r.status_code == 422


def test_list_posts(client, created_post):
    r = client.get("/posts")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) >= 1


def test_get_post(client, created_post):
    r = client.get(f"/posts/{created_post['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created_post["id"]


def test_get_post_not_found(client):
    r = client.get("/posts/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_add_comment(client, created_post):
    r = client.post(
        f"/posts/{created_post['id']}/comments",
        json={"content": "Super post !"},
    )
    assert r.status_code == 201
    assert r.json()["content"] == "Super post !"


def test_toggle_like(client, created_post):
    r = client.post(f"/posts/{created_post['id']}/likes")
    assert r.status_code == 200
    data = r.json()
    assert data["liked"] is True
    assert data["likes_count"] == 1

    r2 = client.post(f"/posts/{created_post['id']}/likes")
    assert r2.status_code == 200
    assert r2.json()["liked"] is False


def test_delete_post(client):
    r = client.post("/posts", json={"content": "À supprimer", "media_urls": []})
    post_id = r.json()["id"]
    rd = client.delete(f"/posts/{post_id}")
    assert rd.status_code == 204
    assert client.get(f"/posts/{post_id}").status_code == 404


def test_profile_upsert(client):
    r = client.patch("/users/me/profile", json={"display_name": "Test User", "bio": "Bio test"})
    assert r.status_code == 200
    assert r.json()["display_name"] == "Test User"
