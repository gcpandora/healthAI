from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSON, UUID

from core.database import Base


class MealAnalysis(Base):
    __tablename__ = "meal_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    image_filename = Column(String(255), nullable=False)
    vision_source = Column(String(50), nullable=False)  # huggingface | google_vision | fallback_manual
    detected_foods = Column(JSON, nullable=False, default=list)
    calories_estimated = Column(Float, nullable=True)
    proteins_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fats_g = Column(Float, nullable=True)
    nutritional_balance = Column(String(50), nullable=False, default="unknown")
    recommendations = Column(JSON, nullable=False, default=list)
    confidence_score = Column(Float, nullable=False, default=0.0)
    is_fallback = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_meal_analyses_user_id", "user_id"),
        Index("idx_meal_analyses_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<MealAnalysis(id={self.id}, source={self.vision_source}, balance={self.nutritional_balance})>"
