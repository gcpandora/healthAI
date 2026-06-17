# 🏥 HealthAI Coach — Backend Métier

> MSPR TPRE501 · CDA / DIADS · EPSI
> Équipe : Tom (DevOps) · Houssem (Data/ML) · Hanane (BDD) · Tojo (API) · Hélie (Frontend)

## 📋 Description du projet

Backend métier de la plateforme **HealthAI Coach**, une startup de santé connectée. Ce projet intègre :
- Un **pipeline ETL** automatisé (collecte, nettoyage, transformation de données)
- Une **base de données PostgreSQL** relationnelle
- Une **API REST** documentée (FastAPI + OpenAPI)
- Un **dashboard interactif** (Metabase) conforme RGAA AA
- Une **interface web d'administration** (frontend)

---

## 🏗️ Architecture

```
healthai-coach/
├── services/
│   ├── api/          # API REST FastAPI (Tojo)
│   ├── etl/          # Pipelines ETL + scripts Python (Houssem)
│   ├── ml/           # Modèles IA / recommandations (Houssem)
│   ├── frontend/     # Interface web d'administration (Hélie)
│   └── dashboard/    # Configuration Metabase (Houssem)
├── database/         # Migrations SQL + seeds (Hanane)
│   ├── migrations/
│   └── seeds/
├── docs/             # Documentation technique
├── .github/          # CI/CD GitHub Actions (Tom)
├── docker-compose.yml
├── docker-compose.dev.yml
└── .env.example
```

---

## 🚀 Démarrage rapide (< 30 minutes)

### Prérequis

- [Docker](https://www.docker.com/get-started) ≥ 24.x
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.x
- [Git](https://git-scm.com/)

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/VOTRE_ORG/healthai-coach.git
cd healthai-coach

# 2. Copier et remplir les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs (voir section Variables d'environnement)

# 3. Lancer tous les services
docker compose up --build

# 4. Vérifier que tout tourne
docker compose ps
```

### Services disponibles après démarrage

| Service     | URL                          | Description                     |
|-------------|------------------------------|---------------------------------|
| API REST    | http://localhost:8000        | FastAPI + doc Swagger            |
| API Docs    | http://localhost:8000/docs   | Documentation OpenAPI           |
| Frontend    | http://localhost:3000        | Interface web d'administration  |
| Metabase    | http://localhost:3001        | Dashboard analytique            |
| PostgreSQL  | localhost:5432               | Base de données                 |
| Adminer     | http://localhost:8080        | Interface BDD (dev uniquement)  |

---

## 🌿 Workflow Git

### Convention de branches

```
main          ← production, protégée (jamais de push direct)
develop       ← intégration (base de travail commune)
feature/prenom-description    ex: feature/tojo-auth-jwt
fix/prenom-description        ex: fix/hanane-migration-v2
```

### Convention de commits (Conventional Commits)

```bash
feat: ajouter endpoint GET /users
fix: corriger la validation des données nutritionnelles
docs: mettre à jour le README avec les instructions Docker
chore: mettre à jour les dépendances Python
refactor: extraire la logique ETL dans un module séparé
test: ajouter les tests unitaires pour l'API utilisateurs
```

### Créer une branche et soumettre une PR

```bash
# Toujours partir de develop
git checkout develop
git pull origin develop

# Créer votre branche
git checkout -b feature/prenom-ma-feature

# ... travailler ...

git add .
git commit -m "feat: description claire de ce que vous avez fait"
git push origin feature/prenom-ma-feature

# Ouvrir une Pull Request vers develop sur GitHub
# Attendre la review de Tom (DevOps) avant de merger
```

---

## 🔧 Variables d'environnement

Copier `.env.example` en `.env` et remplir :

```bash
# Base de données
POSTGRES_DB=healthai_db
POSTGRES_USER=healthai_user
POSTGRES_PASSWORD=CHANGEZ_MOI_EN_PROD

# API
API_SECRET_KEY=CHANGEZ_MOI_EN_PROD
API_DEBUG=true
API_PORT=8000

# Metabase
MB_DB_TYPE=postgres
MB_DB_DBNAME=metabase_db
MB_DB_PORT=5432
MB_DB_USER=metabase_user
MB_DB_PASS=CHANGEZ_MOI_EN_PROD
```

> ⚠️ **IMPORTANT** : Ne jamais commiter le fichier `.env`. Il est dans le `.gitignore`.

---

## 📁 Documentation par module

| Module       | Documentation                         | Responsable |
|--------------|---------------------------------------|-------------|
| ETL          | [docs/etl.md](docs/etl.md)           | Houssem     |
| Base de données | [docs/data-model.md](docs/data-model.md) | Hanane  |
| API REST     | [docs/api.md](docs/api.md)           | Tojo        |
| Frontend     | [docs/frontend.md](docs/frontend.md) | Hélie       |
| Dashboard    | [docs/dashboard.md](docs/dashboard.md) | Houssem   |
| Déploiement  | [docs/deployment.md](docs/deployment.md) | Tom     |

---

## 🧪 Lancer les tests

```bash
# Tests API
docker compose run api pytest

# Tests ETL
docker compose run etl pytest

# Lint (tous les services)
docker compose -f docker-compose.dev.yml run lint
```

---

## 📊 Datasets utilisés

| Dataset | Source | Usage |
|---------|--------|-------|
| Daily Food & Nutrition | Kaggle | Base nutritionnelle |
| Gym Members Exercise | Kaggle | Profils utilisateurs |
| ExerciseDB | GitHub | Catalogue exercices |
| Fitness Tracker | Kaggle | Métriques d'activité |

> Voir [docs/data-sources.md](docs/data-sources.md) pour la justification complète.

---

## 👥 Équipe

| Membre | Rôle | Périmètre |
|--------|------|-----------|
| Tom | DevOps / Lead | Docker, CI/CD, intégration, repo GitHub |
| Houssem | Data Engineer / ML | ETL, nettoyage, visualisation, modèles IA |
| Hanane | DBA | Modèle relationnel, migrations SQL |
| Tojo | Backend Dev | API REST FastAPI, authentification |
| Hélie | Frontend Dev | Interface web d'administration |
