"""
HealthAI Coach — User Model
Modèle SQLAlchemy pour la table users
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, SmallInteger, Numeric, DateTime, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class User(Base):
    """
    Modèle utilisateur HealthAI Coach.
    Représente la table 'users' en base de données.
    """
    __tablename__ = "users"
    
    # ─────────────────────────────────────────────────────────────────
    # Identifiant
    # ─────────────────────────────────────────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    
    # ─────────────────────────────────────────────────────────────────
    # Authentification
    # ─────────────────────────────────────────────────────────────────
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # ─────────────────────────────────────────────────────────────────
    # Données Démographiques
    # ─────────────────────────────────────────────────────────────────
    age = Column(Integer, nullable=True)
    gender = Column(
        String(10),
        nullable=True,
        doc="'male', 'female', 'other'"
    )
    height_cm = Column(Numeric(5, 2), nullable=True)  # Hauteur en cm
    weight_kg = Column(Numeric(5, 2), nullable=True)  # Poids en kg
    
    # ─────────────────────────────────────────────────────────────────
    # Activité de base
    # ─────────────────────────────────────────────────────────────────
    water_intake_liters = Column(Numeric(4, 2), nullable=True)
    workout_frequency = Column(SmallInteger, nullable=True)  # séances/semaine
    fitness_level = Column(
        String(20),
        default="beginner",
        nullable=True,
        doc="beginner, intermediate, advanced"
    )

    # ─────────────────────────────────────────────────────────────────
    # Objectif Personnel
    # ─────────────────────────────────────────────────────────────────
    goal = Column(
        String(50),
        default="general_health",
        nullable=False,
        doc="weight_loss, muscle_gain, sleep_improvement, maintenance, general_health"
    )
    
    # ─────────────────────────────────────────────────────────────────
    # Abonnement
    # ─────────────────────────────────────────────────────────────────
    plan = Column(
        String(20),
        default="free",
        nullable=False,
        doc="free, premium, premium_plus"
    )
    
    # ─────────────────────────────────────────────────────────────────
    # Rôle utilisateur
    # ─────────────────────────────────────────────────────────────────
    role = Column(
        String(20),
        default="user",
        nullable=False,
        doc="user, admin"
    )
    
    # ─────────────────────────────────────────────────────────────────
    # Timestamps
    # ─────────────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # ─────────────────────────────────────────────────────────────────
    # Relations (optionnelles pour le moment)
    # ─────────────────────────────────────────────────────────────────
    # metrics = relationship("UserMetric", back_populates="user", cascade="all, delete-orphan")
    # food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    # workout_logs = relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    
    # ─────────────────────────────────────────────────────────────────
    # Indices pour performances
    # ─────────────────────────────────────────────────────────────────
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_created_at', 'created_at'),
        CheckConstraint("age > 0 AND age < 120", name="check_user_age"),
        CheckConstraint("height_cm > 0", name="check_user_height"),
        CheckConstraint("weight_kg > 0", name="check_user_weight"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"



