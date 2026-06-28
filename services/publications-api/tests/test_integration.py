"""
Tests d'intégration publications-api — scénario complet :
  auth → créer post → upload URL (mock MinIO) → like → commentaire
  → vérifier compteurs

Requiert une base PostgreSQL réelle (voir conftest.py).
"""

from unittest.mock import MagicMock, patch


class TestPublicationsIntegration:
    """Scénario complet exécuté dans l'ordre par pytest."""

    post_id: str = ""

    # ── 1. Santé de l'API ──────────────────────────────────────────────────
    def test_health_endpoint(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    # ── 2. Création de post (auth requise) ────────────────────────────────
    def test_create_post_unauthenticated(self, client):
        r = client.post("/posts", json={"content": "test"})
        assert r.status_code == 401

    def test_create_post(self, client, auth_headers, test_user_id):
        payload = {
            "content": "Post d'intégration — test complet du flux publications",
            "media_urls": [],
        }
        r = client.post("/posts", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["content"] == payload["content"]
        assert str(data["user_id"]) == test_user_id
        assert data["likes_count"] == 0
        assert data["comments_count"] == 0
        TestPublicationsIntegration.post_id = data["id"]

    # ── 3. Upload média (MinIO mocké) ─────────────────────────────────────
    def test_upload_media_mock(self, client, auth_headers):
        mock_s3 = MagicMock()
        mock_s3.put_object.return_value = {}

        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("routers.media._s3_client", return_value=mock_s3):
            r = client.post(
                "/media/upload",
                files={"file": ("test.png", fake_png, "image/png")},
                headers=auth_headers,
            )

        assert r.status_code == 200, r.text
        data = r.json()
        assert "url" in data
        assert "healthai-media" in data["url"]
        mock_s3.put_object.assert_called_once()

    def test_upload_media_invalid_type(self, client, auth_headers):
        r = client.post(
            "/media/upload",
            files={"file": ("evil.exe", b"MZ", "application/octet-stream")},
            headers=auth_headers,
        )
        assert r.status_code == 400

    # ── 4. Like / Unlike ──────────────────────────────────────────────────
    def test_like_post(self, client, auth_headers):
        pid = TestPublicationsIntegration.post_id
        r = client.post(f"/posts/{pid}/like", headers=auth_headers)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["liked"] is True
        assert data["likes_count"] == 1

    def test_like_post_idempotent(self, client, auth_headers):
        """Un deuxième like sur le même post doit unliker (toggle)."""
        pid = TestPublicationsIntegration.post_id
        r = client.post(f"/posts/{pid}/like", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["liked"] is False
        # Re-like pour la suite des tests
        client.post(f"/posts/{pid}/like", headers=auth_headers)

    # ── 5. Commentaire ────────────────────────────────────────────────────
    def test_add_comment(self, client, auth_headers):
        pid = TestPublicationsIntegration.post_id
        payload = {"content": "Commentaire d'intégration — superbe post !"}
        r = client.post(f"/posts/{pid}/comments", json=payload, headers=auth_headers)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["content"] == payload["content"]

    def test_add_comment_too_long(self, client, auth_headers):
        pid = TestPublicationsIntegration.post_id
        r = client.post(
            f"/posts/{pid}/comments",
            json={"content": "x" * 501},
            headers=auth_headers,
        )
        assert r.status_code == 422

    # ── 6. Vérification des compteurs ─────────────────────────────────────
    def test_verify_counters(self, client, auth_headers):
        pid = TestPublicationsIntegration.post_id
        r = client.get("/posts", headers=auth_headers)
        assert r.status_code == 200
        posts = r.json()["items"]
        post = next((p for p in posts if p["id"] == pid), None)
        assert post is not None, "Post introuvable dans la liste"
        assert post["likes_count"] >= 1, "Au moins 1 like attendu"
        assert post["comments_count"] >= 1, "Au moins 1 commentaire attendu"

    def test_get_comments_list(self, client, auth_headers):
        pid = TestPublicationsIntegration.post_id
        r = client.get(f"/posts/{pid}/comments", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["content"] == "Commentaire d'intégration — superbe post !"
