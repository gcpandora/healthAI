import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, TIMESTAMP, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


def _now():
    return datetime.now(timezone.utc)


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(ARRAY(Text), nullable=False, server_default="{}")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=_now)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=_now, onupdate=_now)

    __table_args__ = (
        CheckConstraint("char_length(content) BETWEEN 1 AND 2000", name="posts_content_length"),
    )
