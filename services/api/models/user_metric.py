"""
HealthAI Coach — UserMetric Model
Modèle SQLAlchemy pour la table user_metrics
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class UserMetric(Base):
    """
    Modèle pour la table user_metrics.
    Métriques biométriques et d'activité dans le temps.
    """
    __tablename__ = "user_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Biométrie (Gym Members Dataset)
    weight_kg = Column(Numeric(5, 2), nullable=True)
    body_fat_pct = Column(Numeric(5, 2), nullable=True)
    bmi = Column(Numeric(5, 2), nullable=True)
    heart_rate_avg = Column(Integer, nullable=True)
    heart_rate_max = Column(Integer, nullable=True)
    heart_rate_rest = Column(Integer, nullable=True)

    # Activité quotidienne (Fitness Tracker Dataset)
    steps = Column(Integer, nullable=True)
    active_minutes = Column(Integer, nullable=True)
    calories_burned = Column(Numeric(7, 2), nullable=True)

    # Sommeil
    sleep_hours = Column(Numeric(4, 2), nullable=True)

    __table_args__ = (
        Index('idx_user_metrics_user_id', 'user_id'),
        Index('idx_user_metrics_recorded_at', 'recorded_at'),
    )

    def __repr__(self) -> str:
        return f"<UserMetric(id={self.id}, user_id={self.user_id}, recorded_at={self.recorded_at})>"
