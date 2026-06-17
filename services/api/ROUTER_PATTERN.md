# 📋 GUIDE: Comment Créer un Nouveau Router API

## Template Rapide pour Nutrition & Exercises

Ce guide montre le **pattern standard** utilisé pour Auth + Users.  
Appliquez le même pattern pour **Nutrition** et **Exercises**.

---

## 📐 Pattern Standard (4 fichiers)

### 1️⃣ Model SQLAlchemy (models/nutrition.py) ✅ DÉJÀ CRÉÉ

```python
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from ..core.database import Base

class NutritionItem(Base):
    __tablename__ = "nutrition_items"
    id = Column(..., primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    calories = Column(Numeric(7, 2), nullable=True)
    # ... autres colonnes
```

### 2️⃣ Schemas Pydantic (schemas/nutrition.py) - À CRÉER

```python
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class NutritionItemOut(BaseModel):
    """Réponse GET nutrition item"""
    id: uuid.UUID
    name: str
    calories: Optional[float]
    category: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class NutritionItemCreate(BaseModel):
    """Request POST nutrition item"""
    name: str
    category: Optional[str] = None
    calories: Optional[float] = None
    proteins_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fats_g: Optional[float] = None
    fiber_g: Optional[float] = None

class FoodLogCreate(BaseModel):
    """Request POST food log"""
    nutrition_item_id: uuid.UUID
    quantity_g: float
    meal_type: str  # breakfast, lunch, dinner, snack

class FoodLogOut(BaseModel):
    """Réponse GET food log"""
    id: uuid.UUID
    user_id: uuid.UUID
    nutrition_item_id: uuid.UUID
    quantity_g: float
    meal_type: str
    logged_at: datetime
    
    class Config:
        from_attributes = True
```

### 3️⃣ Router (routers/nutrition.py) - À CRÉER

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.nutrition import NutritionItem, FoodLog
from ..schemas.nutrition import NutritionItemOut, FoodLogCreate, FoodLogOut, NutritionItemCreate

router = APIRouter(prefix="/api/v1", tags=["nutrition"])

# ─── NUTRITION ITEMS ───

@router.get("/nutrition", response_model=list[NutritionItemOut])
async def list_nutrition_items(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str = Query(None),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister les aliments (paginé)"""
    query = db.query(NutritionItem)
    if category:
        query = query.filter(NutritionItem.category == category)
    
    items = query.offset(offset).limit(limit).all()
    return [NutritionItemOut.from_orm(item) for item in items]


@router.get("/nutrition/{item_id}", response_model=NutritionItemOut)
async def get_nutrition_item(
    item_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupérer détail aliment"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")
    
    item = db.query(NutritionItem).filter(NutritionItem.id == item_uuid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")
    return NutritionItemOut.from_orm(item)


@router.post("/nutrition", response_model=NutritionItemOut, status_code=201)
async def create_nutrition_item(
    data: NutritionItemCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Créer aliment (admin)"""
    item = NutritionItem(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return NutritionItemOut.from_orm(item)


# ─── FOOD LOGS ───

@router.get("/users/{target_user_id}/food-logs", response_model=list[FoodLogOut])
async def get_food_logs(
    target_user_id: str,
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupérer les logs alimentaires d'un utilisateur"""
    logs = db.query(FoodLog).filter(
        FoodLog.user_id == target_user_id
    ).order_by(FoodLog.logged_at.desc()).limit(limit).all()
    
    return [FoodLogOut.from_orm(log) for log in logs]


@router.post("/users/{target_user_id}/food-logs", response_model=FoodLogOut, status_code=201)
async def create_food_log(
    target_user_id: str,
    data: FoodLogCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logger un aliment"""
    log = FoodLog(
        user_id=target_user_id,
        **data.dict()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return FoodLogOut.from_orm(log)
```

### 4️⃣ Ajouter dans main.py

```python
# Au début du fichier
from models.nutrition import NutritionItem, FoodLog  # noqa: F401

# En bas (avec les autres routers)
from routers import auth, users, nutrition
app.include_router(nutrition.router)
```

---

## ✅ Checklist pour Créer Nutrition Router

- [ ] Créer `services/api/schemas/nutrition.py`
  - [ ] `NutritionItemOut` (réponse GET)
  - [ ] `NutritionItemCreate` (request POST)
  - [ ] `FoodLogCreate` (request POST log)
  - [ ] `FoodLogOut` (réponse GET log)

- [ ] Créer `services/api/routers/nutrition.py`
  - [ ] GET `/api/v1/nutrition` (liste paginée)
  - [ ] GET `/api/v1/nutrition/{item_id}` (détail)
  - [ ] POST `/api/v1/nutrition` (créer)
  - [ ] GET `/api/v1/users/{user_id}/food-logs` (liste logs)
  - [ ] POST `/api/v1/users/{user_id}/food-logs` (créer log)

- [ ] Importer les modèles dans `main.py`
- [ ] Importer le router dans `main.py`

- [ ] Tester via Swagger: http://localhost:8000/docs

**Durée estimée:** 45-60 min

---

## ✅ Checklist pour Créer Exercises Router

Même pattern que Nutrition, avec:

- [ ] Créer `services/api/schemas/exercise.py`
  - [ ] `ExerciseOut`
  - [ ] `ExerciseCreate`
  - [ ] `WorkoutLogCreate`
  - [ ] `WorkoutLogOut`

- [ ] Créer `services/api/routers/exercises.py`
  - [ ] GET `/api/v1/exercises` (liste, filtrable par type/difficulty)
  - [ ] GET `/api/v1/exercises/{exercise_id}` (détail)
  - [ ] POST `/api/v1/exercises` (créer)
  - [ ] GET `/api/v1/users/{user_id}/workout-logs` (historique)
  - [ ] POST `/api/v1/users/{user_id}/workout-logs` (logger exercice)

- [ ] Importer dans `main.py`
- [ ] Tester via Swagger

**Durée estimée:** 45-60 min

---

## 🎯 Règles Standard

### Tous les Routers Doivent:

1. **Utiliser UUID pour IDs**
   ```python
   target_uuid = uuid.UUID(item_id)
   ```

2. **Toujours vérifier authentification**
   ```python
   user_id: str = Depends(get_current_user)
   ```

3. **Utiliser HTTP codes corrects**
   - 200 GET ✓
   - 201 POST ✓
   - 204 DELETE ✓
   - 400 Erreur validation
   - 401 Non authentifié
   - 404 Non trouvé

4. **Paginer les listes**
   ```python
   limit: int = Query(20, ge=1, le=100)
   offset: int = Query(0, ge=0)
   ```

5. **Documenter chaque endpoint**
   ```python
   @router.get("/path", summary="Titre court", tags=["catégorie"])
   async def endpoint():
       """Description détaillée de ce que fait cet endpoint."""
   ```

6. **Utiliser Schemas Pydantic**
   - Pour requests: `NutritionItemCreate`
   - Pour responses: `NutritionItemOut`
   - Toujours avec `response_model=...`

7. **Importer depuis le bon endroit**
   ```python
   from ..core.database import get_db
   from ..models.nutrition import NutritionItem
   from ..schemas.nutrition import NutritionItemOut
   ```

---

## 🧪 Test Rapide d'un Endpoint

Une fois créé, tester directement depuis Swagger:

1. Swagger: http://localhost:8000/docs
2. Chercher le nouvel endpoint
3. "Try it out"
4. Remplir les paramètres
5. "Execute"

Ou en cURL:

```bash
# Lister nutrition items
curl -X GET "http://localhost:8000/api/v1/nutrition?limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Créer aliment
curl -X POST "http://localhost:8000/api/v1/nutrition" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pomme",
    "category": "Fruits",
    "calories": 52.0,
    "proteins_g": 0.3,
    "carbs_g": 14.0,
    "fats_g": 0.2,
    "fiber_g": 2.4
  }'
```

---

## 📊 Standard Response Format

**Success (200/201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Pomme",
  "calories": 52.0,
  "created_at": "2026-03-30T10:00:00+00:00"
}
```

**List (200):**
```json
[
  {"id": "...", "name": "Pomme", "calories": 52.0},
  {"id": "...", "name": "Banana", "calories": 89.0}
]
```

**Error (4xx/5xx):**
```json
{
  "detail": "Message d'erreur explicite"
}
```

---

## 💡 Tips & Tricks

1. **Copier/coller depuis user.py est OK** - C'est le pattern standard
2. **Utiliser la même structure de fichiers**
3. **Tester immédiatement dans Swagger après création**
4. **Commit régulier dans git**
5. **Si une dépendance Python manque**, elle est sûrement dans `requirements.txt` déjà

---

## 🎓 Apprendre Plus

- Docs FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy ORM: https://docs.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev

---

**Version:** 1.0  
**Dernière mise à jour:** 30 mars 2026  
**Créé par:** Tojo  
