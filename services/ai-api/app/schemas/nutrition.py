from pydantic import BaseModel, Field
from typing import Optional, List


class NutritionAnalyzeRequest(BaseModel):
    description: Optional[str] = Field(None, description="Description texte du repas")
    health_goal: str = Field("equilibre", description="Objectif santé de l'utilisateur")


class FoodItem(BaseModel):
    nom: str
    quantite: str
    calories: int


class Macros(BaseModel):
    calories: int
    proteines: float
    glucides: float
    lipides: float = 0.0


class NutritionAnalyzeResponse(BaseModel):
    aliments: List[FoodItem]
    nutrition: Macros
    score_sante: int = Field(..., ge=1, le=10)
    desequilibres: List[str] = []
    conseils: List[str] = []
    source: str = "ollama"


class MealPlanRequest(BaseModel):
    objectif: str = Field("equilibre", description="perte_poids | prise_masse | equilibre")
    calories_cible: int = Field(2000, ge=1000, le=5000)
    duree_jours: int = Field(7, ge=1, le=14)
    budget: Optional[str] = Field(None, description="faible | moyen | eleve")
    regime: Optional[str] = Field(None, description="vegetarien | vegan | sans_gluten")
    allergies: List[str] = []


class Repas(BaseModel):
    nom: str
    calories: int
    ingredients: List[str]


class JourPlan(BaseModel):
    jour: int
    petit_dejeuner: Repas
    dejeuner: Repas
    diner: Repas
    total_calories: int


class MealPlanResponse(BaseModel):
    plan: List[JourPlan]
    source: str = "ollama"
