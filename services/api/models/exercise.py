"""
HealthAI Coach — Exercise Model
Modèle SQLAlchemy pour exercises et workout_logs
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class Exercise(Base):
    """
    Modèle pour la table exercises.
    Représente le catalogue d'exercices disponibles.
    """
    __tablename__ = "exercises"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=True)  # cardio, strength, flexibility, etc.
    muscle_group = Column(String(100), nullable=True)  # chest, legs, arms, etc.
    equipment = Column(String(100), nullable=True)  # dumbbell, barbell, machine, etc.
    difficulty = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    instructions = Column(Text, nullable=True)
    
    # Référence externe (ex: ExerciseDB API)
    external_id = Column(String(100), nullable=True)
    source = Column(String(100), nullable=True)  # ex: "ExerciseDB"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index('idx_exercise_name', 'name'),
        Index('idx_exercise_type', 'type'),
        Index('idx_exercise_difficulty', 'difficulty'),
    )


class WorkoutLog(Base):
    """
    Modèle pour la table workout_logs.
    Représente les exercices effectués par les utilisateurs.
    """
    __tablename__ = "workout_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    
    duration_min = Column(Integer, nullable=False)  # Durée en minutes
    sets = Column(Integer, nullable=True)  # Nombre de séries (pour strength)
    reps = Column(Integer, nullable=True)  # Répétitions par série
    calories_burned = Column(Numeric(7, 2), nullable=True)
    logged_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index('idx_workout_log_user', 'user_id'),
        Index('idx_workout_log_date', 'logged_at'),
    )
