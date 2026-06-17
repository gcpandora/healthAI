# Backend API - HealthAI Coach  

## 🎯 État Actuel

✅ **Fonctionnalités complétées:**
- **Système admin complet** : rôles user/admin, endpoints admin, auto-création admin
- **Authentification JWT** : login/register/profile avec tokens sécurisés
- **CRUD complet** : Users, Nutrition, Exercises avec logs
- **Métriques globales** : statistiques admin (admin only)
- **Sécurité renforcée** : hashage bcrypt, validation Pydantic, RBAC
- **Tests fonctionnels** : test_admin.py pour validation basique
- **Documentation complète** : BACKEND_DOCUMENTATION.md à jour

### Admin par défaut
- **Email** : `admin@healthai.com`
- **Mot de passe** : `admin123`
- **Créé automatiquement** au premier démarrage

## 🚀 Lancer l'API

### 1. Prérequis

```bash
# Les dépendances sont listées dans requirements.txt
# Assurez-vous d'être dans le bon dossier
cd services/api
```

### 2. Variables d'environnement

```bash
# Copier le .env.example en .env (à la racine du projet)
cp ../../.env.example ../../.env

# Editer .env avec vos valeurs (docker-compose le fera automatiquement)
```

### 3. Avec Docker Compose (recommandé)

```bash
cd ../../..  # Aller à la racine healthAI
docker-compose up api
```

L'API démarre sur `http://localhost:8000`

### 4. Sans Docker (développement local)

```bash
# Installer les dépendances
pip install -r requirements.txt

# S'assurer que PostgreSQL tourne
# Puis lancer avec uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Endpoints Disponibles

### Documentation Interactive

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints principaux

#### Authentication
```
POST   /auth/register            - Créer un compte
POST   /auth/login               - Se connecter
GET    /auth/profile             - Récupérer profil (protégé)
PUT    /auth/profile             - Mettre à jour profil (protégé)
POST   /auth/logout              - Déconnexion (protégé)
```

#### Users (CRUD + Admin)
```
GET    /api/v1/users             - Lister utilisateurs (paginé)
GET    /api/v1/users/{user_id}   - Récupérer utilisateur
POST   /api/v1/users             - Créer utilisateur (admin)
PUT    /api/v1/users/{user_id}   - Mettre à jour (admin)
DELETE /api/v1/users/{user_id}   - Supprimer (admin)
POST   /api/v1/users/{user_id}/promote - Promouvoir admin (admin)
```

#### Nutrition (CRUD + Logs)
```
GET    /api/v1/nutrition                    - Lister aliments
GET    /api/v1/nutrition/{id}               - Détail aliment
POST   /api/v1/nutrition                    - Créer aliment (admin)
PUT    /api/v1/nutrition/{id}               - Modifier aliment (admin)
DELETE /api/v1/nutrition/{id}               - Supprimer aliment (admin)
GET    /api/v1/users/{id}/food-logs         - Logs nourriture utilisateur
POST   /api/v1/users/{id}/food-logs         - Ajouter log nourriture
DELETE /api/v1/users/{id}/food-logs/{id}    - Supprimer log nourriture
GET    /api/v1/admin/food-logs              - Tous les logs nourriture (admin)
```

#### Exercises (CRUD + Logs)
```
GET    /api/v1/exercises                    - Lister exercices
GET    /api/v1/exercises/{id}               - Détail exercice
POST   /api/v1/exercises                    - Créer exercice (admin)
PUT    /api/v1/exercises/{id}               - Modifier exercice (admin)
DELETE /api/v1/exercises/{id}               - Supprimer exercice (admin)
GET    /api/v1/users/{id}/workout-logs      - Logs entraînement utilisateur
POST   /api/v1/users/{id}/workout-logs      - Ajouter log entraînement
DELETE /api/v1/users/{id}/workout-logs/{id} - Supprimer log entraînement
GET    /api/v1/admin/workout-logs           - Tous les logs entraînement (admin)
```

#### Metrics (Admin uniquement)
```
GET    /api/v1/metrics                      - Métriques globales (admin)
GET    /api/v1/metrics/users/{id}           - Métriques utilisateur (admin)
```

### Exemple: Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "password": "securepass123",
    "age": 28,
    "goal": "weight_loss"
  }'
```

Réponse:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "alice@example.com",
    "username": "alice",
    "age": 28,
    "goal": "weight_loss",
    "plan": "free",
    "created_at": "2026-03-30T10:00:00+00:00",
    "updated_at": "2026-03-30T10:00:00+00:00"
  }
}
```

### Exemple: Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepass123"
  }'
```

### Exemple: Récupérer Profil (protégé)

```bash
curl -X GET http://localhost:8000/auth/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Exemple: Lister Utilisateurs

```bash
# Sans filtres
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Avec pagination
curl -X GET "http://localhost:8000/api/v1/users?limit=20&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Avec filtres
curl -X GET "http://localhost:8000/api/v1/users?goal=weight_loss&plan=premium" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## � Sécurité et Rôles

### Système d'authentification
- **JWT Tokens** avec expiration 24h
- **Hashage bcrypt** pour les mots de passe
- **Validation Pydantic** sur toutes les entrées

### Rôles utilisateur
- **user** : utilisateur standard (défaut)
- **admin** : administrateur avec accès complet

### Endpoints admin (marqués 🔐)
- Création/modification/suppression d'utilisateurs
- Gestion du catalogue nutrition/exercices
- Accès aux logs de tous les utilisateurs
- Métriques globales de l'application

### Codes d'erreur
- `401 Unauthorized` : token manquant ou invalide
- `403 Forbidden` : accès admin refusé
- `404 Not Found` : ressource inexistante
- `400 Bad Request` : données invalides

## 🧪 Tests

### Tests existants
```bash
# Test fonctionnel admin
python test_admin.py

# Tests unitaires (à implémenter)
pytest tests/
```

### Couverture de test à implémenter
- ✅ Authentification (login/register/profile)
- ✅ CRUD Users avec permissions admin
- ✅ CRUD Nutrition avec logs
- ✅ CRUD Exercises avec logs
- 🔄 Métriques admin
- 🔄 Validation des données
- 🔄 Gestion d'erreurs

---

### 1. URL API

Depuis le frontend React, utilisez:

```javascript
// services/api.js
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

export const login = (email, password) =>
  axios.post(`${API_URL}/auth/login`, { email, password });

export const register = (userData) =>
  axios.post(`${API_URL}/auth/register`, userData);

export const getProfile = (token) =>
  axios.get(`${API_URL}/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` }
  });
```

### 2. Authentification JWT

Le frontend reçoit un JWT token. À stocker et renvoyer à chaque requête:

```javascript
// Stockage
localStorage.setItem('access_token', response.data.access_token);

// Utilisation
const token = localStorage.getItem('access_token');
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### 3. AuthContext (déjà existant)

[AuthContext.jsx](../frontend/src/contexts/AuthContext.jsx) gère déjà le JWT et les appels API.

## 📊 Base de Données

### Tables créées automatiquement

```sql
-- Exécutées au démarrage de l'API
CREATE TABLE users (...)
CREATE TABLE nutrition_items (...)
CREATE TABLE food_logs (...)
CREATE TABLE exercises (...)
CREATE TABLE workout_logs (...)
```

Visualiser dans Adminer (développement):
- URL: http://localhost:8080
- Serveur: postgres
- User: healthai_user
- Password: [voir .env]
- Database: healthai_db

Ou avec Metabase (analytics):
- URL: http://localhost:3001

## 🧪 Tests

```bash
# Lancer les tests pytest
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=. --cov-report=html
```

## 📝 Structure Code

```
services/api/
├── core/
│   ├── config.py        ✅ Configuration globale
│   ├── database.py      ✅ SQLAlchemy setup
│   └── security.py      ✅ JWT + Password hashing
├── models/
│   ├── user.py          ✅ User model (ORM)
│   ├── nutrition.py     ✅ NutritionItem + FoodLog models
│   └── exercise.py      ✅ Exercise + WorkoutLog models
├── schemas/
│   └── user.py          ✅ Pydantic validation schemas
├── routers/
│   ├── auth.py          ✅ Login, register, profile
│   ├── users.py         ✅ CRUD utilisateurs
│   ├── nutrition.py     ⏳ À créer (pattern: user.py + auth.py)
│   └── exercises.py     ⏳ À créer (pattern: user.py + auth.py)
├── tests/
│   ├── test_auth.py     ⏳ Tests authentification
│   └── test_users.py    ⏳ Tests CRUD
├── main.py              ✅ Point d'entrée FastAPI
└── requirements.txt     ✅ Dépendances Python
```

## 🎯 Prochaines Étapes

1. **Nutrition Router** (~1 heure)
   - Créer `routers/nutrition.py` similaire à `routers/user.py`
   - Endpoints: GET/POST nutrition items, GET/POST food logs
   - Schemas: `NutritionItemOut`, `FoodLogCreate`, etc.

2. **Exercises Router** (~1 heure)
   - Créer `routers/exercises.py`
   - Endpoints: GET/POST exercises, GET/POST workout logs

3. **Metrics Router** (~1 heure)
   - Endpoints de statistiques (top foods, top exercises, etc.)

4. **Tests** (~2 heures)
   - Test fixtures pour users
   - Tests endpoints auth + CRUD

5. **Frontend Integration** (~2 heures)
   - Pages Nutrition et Exercises
   - Admin Dashboard

## 🔒 Sécurité

✅ **Implémenté:**
- JWT tokens (24h expiration)
- Password hashing (bcrypt)
- Protected routes (`Depends(get_current_user)`)
- CORS configuré
- Input validation (Pydantic)

⚠️ **À ajouter:**
- Rate limiting
- Logging des erreurs sécurité
- HTTPS en production
- Refresh tokens

## 📞 Support

Pour questions ou problèmes:
- Swagger docs: http://localhost:8000/docs
- Vérifier les logs du container Docker
- Vérifier la connection BD (Adminer)

---

**Responsable:** Tojo  
**Dernière mise à jour:** 30 mars 2026
