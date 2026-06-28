import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


def _now():
    return datetime.now(timezone.utc)


class Like(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="likes_unique_per_user_post"),
    )
