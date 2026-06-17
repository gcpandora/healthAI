import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from routers.vision_router import RATE_WINDOW, _rate_store

BASE = "/api/v1/vision"

AI_API_SUCCESS = {
    "aliments": [
        {"nom": "Poulet grillé", "quantite": "150g"},
        {"nom": "Riz blanc", "quantite": "100g"},
    ],
    "nutrition": {
        "calories": 420.0,
        "proteines": 35.0,
        "glucides": 45.0,
        "lipides": 8.0,
    },
    "conseils": [
        "Bonne source de protéines.",
        "Pensez à ajouter des légumes.",
    ],
    "score_sante": 7.5,
    "source": "huggingface",
}


def make_mock_client(json_data=None, status_code=200, raise_exc=None):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    if raise_exc:
        mock_response.raise_for_status.side_effect = raise_exc
    else:
        mock_response.raise_for_status.return_value = None

    mock_post = AsyncMock(return_value=mock_response)
    mock_client_instance = AsyncMock()
    mock_client_instance.post = mock_post
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)

    mock_class = MagicMock(return_value=mock_client_instance)
    return mock_class


# ---------------------------------------------------------------------------
# Groupe 1 — analyze-meal avec description texte (pas d'image)
# ---------------------------------------------------------------------------

def test_analyze_meal_text_success(client):
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=AI_API_SUCCESS)):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "poulet riz", "health_goal": "equilibre"})
    assert r.status_code == 200
    data = r.json()
    assert len(data["detected_foods"]) >= 1
    assert "nutrition" in data
    assert data["nutrition"]["calories"] > 0
    assert "analysis_id" in data
    uuid.UUID(data["analysis_id"])
    assert "X-RateLimit-Remaining" in r.headers
    assert data["is_fallback"] is False
    assert data["source"] == "huggingface"


def test_analyze_meal_returns_balance(client):
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=AI_API_SUCCESS)):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "repas test"})
    assert r.status_code == 200
    assert r.json()["balance"] == "balanced"


def test_analyze_meal_protein_deficit(client):
    ai_response = {
        **AI_API_SUCCESS,
        "nutrition": {**AI_API_SUCCESS["nutrition"], "proteines": 10.0},
        "score_sante": 4.0,
    }
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=ai_response)):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "salade légère"})
    assert r.status_code == 200
    assert r.json()["balance"] == "protein_deficit"


def test_analyze_meal_carb_excess(client):
    ai_response = {
        **AI_API_SUCCESS,
        "nutrition": {**AI_API_SUCCESS["nutrition"], "glucides": 150.0, "proteines": 30.0},
        "score_sante": 4.0,
    }
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=ai_response)):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "pâtes en excès"})
    assert r.status_code == 200
    assert r.json()["balance"] == "carb_excess"


# ---------------------------------------------------------------------------
# Groupe 2 — Fallback (ai-api indisponible)
# ---------------------------------------------------------------------------

def test_analyze_meal_fallback_on_timeout(client):
    with patch("routers.vision_router.httpx.AsyncClient",
               make_mock_client(raise_exc=httpx.TimeoutException("timeout"))):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "test timeout"})
    assert r.status_code == 200
    data = r.json()
    assert data["is_fallback"] is True
    assert data["source"] == "fallback_manual"
    assert data.get("message")


def test_analyze_meal_fallback_on_connection_error(client):
    with patch("routers.vision_router.httpx.AsyncClient",
               make_mock_client(raise_exc=httpx.ConnectError("connection refused"))):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "test connexion"})
    assert r.status_code == 200
    assert r.json()["is_fallback"] is True


def test_analyze_meal_fallback_on_http_error(client):
    exc = httpx.HTTPStatusError(
        "503 Service Unavailable",
        request=httpx.Request("POST", "http://ai-api:8002/nutrition/analyze"),
        response=httpx.Response(503),
    )
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(raise_exc=exc)):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "test http 503"})
    assert r.status_code == 200
    assert r.json()["is_fallback"] is True


# ---------------------------------------------------------------------------
# Groupe 3 — Rate limiting
# ---------------------------------------------------------------------------

def test_rate_limit_header_present(client):
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=AI_API_SUCCESS)):
        r = client.post(f"{BASE}/analyze-meal", data={"description": "header check"})
    assert r.status_code == 200
    assert "X-RateLimit-Remaining" in r.headers
    assert int(r.headers["X-RateLimit-Remaining"]) >= 0


def test_rate_limit_exceeded(client):
    ip = "testclient"
    _rate_store[ip] = [time.time()] * 10
    try:
        r = client.post(f"{BASE}/analyze-meal", data={"description": "limite atteinte"})
        assert r.status_code == 429
    finally:
        _rate_store.pop(ip, None)


# ---------------------------------------------------------------------------
# Groupe 4 — GET analyze-meal/{analysis_id}
# ---------------------------------------------------------------------------

def test_get_analysis_success(client):
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=AI_API_SUCCESS)):
        post_r = client.post(f"{BASE}/analyze-meal", data={"description": "analyse à retrouver"})
    assert post_r.status_code == 200
    analysis_id = post_r.json()["analysis_id"]

    get_r = client.get(f"{BASE}/analyze-meal/{analysis_id}")
    assert get_r.status_code == 200
    data = get_r.json()
    assert data["analysis_id"] == analysis_id
    assert data["source"] == "huggingface"
    assert data["is_fallback"] is False


def test_get_analysis_not_found(client):
    r = client.get(f"{BASE}/analyze-meal/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert "detail" in r.json()


# ---------------------------------------------------------------------------
# Groupe 5 — Validation entrée
# ---------------------------------------------------------------------------

def test_analyze_meal_no_input(client):
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=AI_API_SUCCESS)):
        r = client.post(f"{BASE}/analyze-meal", data={})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Groupe 6 — Upload multipart/form-data (fichier image réel)
# ---------------------------------------------------------------------------

def test_analyze_meal_multipart_file_upload(client):
    fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 64  # header JPEG minimal
    with patch("routers.vision_router.httpx.AsyncClient", make_mock_client(json_data=AI_API_SUCCESS)):
        r = client.post(
            f"{BASE}/analyze-meal",
            files={"file": ("repas.jpg", fake_image, "image/jpeg")},
            data={"description": "photo de repas", "health_goal": "equilibre"},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["is_fallback"] is False
    assert data["source"] == "huggingface"
    assert len(data["detected_foods"]) >= 1
    uuid.UUID(data["analysis_id"])


def test_analyze_meal_file_too_large_returns_413(client):
    large_file = b"\x00" * (5 * 1024 * 1024 + 1)  # 5 MB + 1 octet
    r = client.post(
        f"{BASE}/analyze-meal",
        files={"file": ("big.jpg", large_file, "image/jpeg")},
    )
    assert r.status_code == 413
    assert "detail" in r.json()


def test_analyze_meal_unsupported_format_pdf_returns_422(client):
    r = client.post(
        f"{BASE}/analyze-meal",
        files={"file": ("document.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert r.status_code == 422
    assert "detail" in r.json()


def test_analyze_meal_unsupported_format_txt_returns_422(client):
    r = client.post(
        f"{BASE}/analyze-meal",
        files={"file": ("data.txt", b"just text", "text/plain")},
    )
    assert r.status_code == 422
    assert "detail" in r.json()


def test_analyze_meal_corrupted_image_triggers_fallback(client):
    corrupt_bytes = b"\x00\x01\x02\x03"  # pas une image valide
    with patch(
        "routers.vision_router.httpx.AsyncClient",
        make_mock_client(raise_exc=Exception("Image decode error")),
    ):
        r = client.post(
            f"{BASE}/analyze-meal",
            files={"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")},
        )
    assert r.status_code == 200  # pas de 500
    data = r.json()
    assert data["is_fallback"] is True
    assert data["source"] == "fallback_manual"
