from pydantic import BaseModel, Field
from typing import List, Optional


class ActivityRecommendRequest(BaseModel):
    objectif: str = Field("forme_generale", description="perte_poids | prise_masse | endurance | forme_generale")
    niveau: str = Field("debutant", description="debutant | intermediaire | avance")
    duree_seance_min: int = Field(45, ge=15, le=120)
    equipements: List[str] = []
    limitations: List[str] = []


class Exercice(BaseModel):
    nom: str
    series: int
    repetitions: str
    repos_sec: int = 60


class JourEntrainement(BaseModel):
    jour: int
    type_seance: str
    exercices: List[Exercice]
    duree_estimee_min: int


class ActivityRecommendResponse(BaseModel):
    programme: List[JourEntrainement]
    conseils: List[str] = []
    source: str = "ollama"
