import httpx
import json
from app.config import settings


async def generate(system_prompt: str, user_message: str) -> dict:
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
        "format": "json",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{settings.ollama_url}/api/chat", json=payload)
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return json.loads(content)


async def ping() -> float:
    import time
    start = time.time()
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(f"{settings.ollama_url}/api/tags")
        r.raise_for_status()
    return round((time.time() - start) * 1000, 2)
