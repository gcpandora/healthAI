from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import (
    Column,
    String,
    Numeric,
    ForeignKey,

)
from core.database import Base

class FoodLog(Base):
    """
    Modèle pour la table food_logs.
    Représente les aliments loggés par les utilisateurs.
    """
    __tablename__ = "food_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    nutrition_item_id = Column(UUID(as_uuid=True), ForeignKey("nutrition_items.id"), nullable=False)
    
    quantity_g = Column(Numeric(7, 2), nullable=False)  # Quantité en grammes
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    logged_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index('idx_food_log_user', 'user_id'),
        Index('idx_food_log_date', 'logged_at'),
    )