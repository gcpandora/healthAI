import httpx
import time
from app.config import settings

HF_API_URL = f"https://api-inference.huggingface.co/models/{settings.hf_model}"


async def classify_image(image_bytes: bytes) -> list[str]:
    if settings.mock_hf:
        return ["apple", "banana", "chicken breast", "rice", "salad"]
    headers = {"Authorization": f"Bearer {settings.hf_token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(HF_API_URL, headers=headers, content=image_bytes)
        r.raise_for_status()
        results = r.json()
        return [item["label"] for item in results[:5]]


async def ping() -> float:
    if settings.mock_hf:
        return 0.0
    start = time.time()
    headers = {"Authorization": f"Bearer {settings.hf_token}"}
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(
            f"https://api-inference.huggingface.co/models/{settings.hf_model}",
            headers=headers,
        )
        r.raise_for_status()
    return round((time.time() - start) * 1000, 2)
