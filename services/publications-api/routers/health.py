from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "publications-api", "version": "1.0.0"}
