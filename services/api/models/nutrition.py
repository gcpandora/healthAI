"""
HealthAI Coach — Nutrition Model
Modèle SQLAlchemy pour nutrition_items et food_logs
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class NutritionItem(Base):
    """
    Modèle pour la table nutrition_items.
    Représente des aliments avec leurs valeurs nutritionnelles.
    """
    __tablename__ = "nutrition_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    
    meal_type = Column(String(50), nullable=True)  # breakfast, lunch, dinner, snack

    # Macronutriments (pour 100g)
    calories = Column(Numeric(7, 2), nullable=True)
    proteins_g = Column(Numeric(7, 2), nullable=True)
    carbs_g = Column(Numeric(7, 2), nullable=True)
    fats_g = Column(Numeric(7, 2), nullable=True)
    fiber_g = Column(Numeric(7, 2), nullable=True)

    # Micronutriments
    sugar_g = Column(Numeric(7, 2), nullable=True)
    sodium_mg = Column(Numeric(7, 2), nullable=True)
    cholesterol_mg = Column(Numeric(7, 2), nullable=True)
    water_ml = Column(Numeric(7, 2), nullable=True)

    # Source des données
    source = Column(String(100), nullable=True)  # ex: "Kaggle", "USDA"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index('idx_nutrition_name', 'name'),
        Index('idx_nutrition_category', 'category'),
    )



