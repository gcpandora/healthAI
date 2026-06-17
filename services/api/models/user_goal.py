"""
HealthAI Coach — UserGoal Model
Modèle SQLAlchemy pour la table user_goals
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class UserGoal(Base):
    """
    Modèle pour la table user_goals.
    Objectifs personnalisés et traçabilité de leur évolution.
    """
    __tablename__ = "user_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    goal_type = Column(String(50), nullable=True, doc="weight_loss, muscle_gain, maintenance, sleep_improvement, general_health")
    target_value = Column(Numeric(7, 2), nullable=True)  # ex: 70.00 pour poids cible en kg
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index('idx_user_goals_user_id', 'user_id'),
        CheckConstraint(
            "goal_type IN ('weight_loss', 'muscle_gain', 'maintenance', 'sleep_improvement', 'general_health')",
            name="check_user_goal_type"
        ),
    )

    def __repr__(self) -> str:
        return f"<UserGoal(id={self.id}, user_id={self.user_id}, goal_type={self.goal_type})>"
