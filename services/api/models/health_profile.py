"""
HealthAI Coach — HealthProfile Model
Modèle SQLAlchemy pour la table health_profiles
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Numeric, SmallInteger, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class HealthProfile(Base):
    """
    Modèle pour la table health_profiles.
    Données médicales et diététiques par utilisateur (Diet Recommendations Dataset).
    """
    __tablename__ = "health_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Profil médical
    disease_type = Column(String(100), nullable=True)
    severity = Column(String(10), nullable=True, doc="mild, moderate, severe")
    physical_activity_level = Column(String(10), nullable=True, doc="low, moderate, high")
    cholesterol_mg_dl = Column(Numeric(6, 2), nullable=True)
    blood_pressure_mmhg = Column(SmallInteger, nullable=True)
    glucose_mg_dl = Column(Numeric(6, 2), nullable=True)

    # Préférences alimentaires
    dietary_restrictions = Column(String(200), nullable=True)
    allergies = Column(String(200), nullable=True)
    preferred_cuisine = Column(String(100), nullable=True)

    # Métriques de suivi
    weekly_exercise_hours = Column(Numeric(4, 1), nullable=True)
    adherence_to_diet_plan = Column(Numeric(5, 2), nullable=True)
    dietary_nutrient_imbalance_score = Column(Numeric(4, 2), nullable=True)

    # Recommandation générée
    diet_recommendation = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index('idx_health_profiles_user_id', 'user_id'),
        CheckConstraint("severity IN ('mild', 'moderate', 'severe')", name="check_health_profile_severity"),
        CheckConstraint("physical_activity_level IN ('low', 'moderate', 'high')", name="check_health_profile_activity"),
    )

    def __repr__(self) -> str:
        return f"<HealthProfile(id={self.id}, user_id={self.user_id})>"
