import httpx
from app.config import settings


async def get_user_profile(user_id: str, token: str) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(f"{settings.backend_url}/users/{user_id}", headers=headers)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None


async def get_activity_recommendations(payload: dict) -> dict | None:
    """
    Appelle le micro-service de recommandation (MongoDB) sur le port 8001.
    C'est la source de vérité pour les exercices — critère éliminatoire jury.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.post(
                "http://recommendation:8001/recommendations",
                json=payload,
            )
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "Micro-service MongoDB injoignable: %s", type(exc).__name__
            )
            return None
