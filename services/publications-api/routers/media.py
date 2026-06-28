import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from core.config import settings
from core.security import get_current_user

router = APIRouter(prefix="/media", tags=["media"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "video/mp4"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 Mo

_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "video/mp4": "mp4",
}


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
    )


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type non autorisé : {file.content_type}. Types acceptés : image/jpeg, image/png, image/webp, video/mp4",
        )

    content = await file.read()

    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Fichier trop volumineux (max 10 Mo)",
        )

    ext = _EXT[file.content_type]
    key = f"posts/{user_id}/{uuid.uuid4()}.{ext}"

    try:
        s3 = _s3_client()
        s3.put_object(
            Bucket=settings.minio_bucket,
            Key=key,
            Body=content,
            ContentType=file.content_type,
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(status_code=502, detail=f"Erreur stockage objet : {exc}") from exc

    url = f"http://{settings.minio_endpoint}/{settings.minio_bucket}/{key}"
    return {"url": url}
