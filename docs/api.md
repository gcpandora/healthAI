# API REST — HealthAI Coach
Responsable : Tojo

## Architecture FastAPI

```
services/api/
├── main.py               ← point d'entrée (déjà créé)
├── Dockerfile            ← déjà créé
├── requirements.txt      ← déjà créé
├── routers/
│   ├── __init__.py
│   ├── users.py          ← CRUD utilisateurs
│   ├── nutrition.py      ← aliments, logs alimentaires
│   ├── exercises.py      ← catalogue exercices
│   └── metrics.py        ← métriques biométriques
├── models/
│   ├── __init__.py
│   ├── user.py           ← modèles SQLAlchemy
│   ├── nutrition.py
│   ├── exercise.py
│   └── metric.py
├── schemas/
│   ├── __init__.py
│   ├── user.py           ← schémas Pydantic (validation)
│   ├── nutrition.py
│   ├── exercise.py
│   └── metric.py
├── core/
│   ├── config.py         ← variables d'environnement
│   ├── database.py       ← connexion SQLAlchemy
│   └── security.py       ← JWT, hachage mots de passe
└── tests/
    ├── test_users.py
    ├── test_nutrition.py
    └── test_exercises.py
```

## Endpoints cibles

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | /api/v1/users | Lister les utilisateurs |
| POST | /api/v1/users | Créer un utilisateur |
| GET | /api/v1/users/{id} | Détails d'un utilisateur |
| PUT | /api/v1/users/{id} | Modifier un utilisateur |
| DELETE | /api/v1/users/{id} | Supprimer un utilisateur |
| GET | /api/v1/nutrition | Lister les aliments |
| GET | /api/v1/exercises | Lister les exercices |
| GET | /api/v1/metrics/{user_id} | Métriques d'un utilisateur |
| POST | /api/v1/metrics | Enregistrer des métriques |

## Sécurité
- Authentification JWT Bearer Token
- Hachage bcrypt des mots de passe
- Validation des données via Pydantic

## Documentation
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc
