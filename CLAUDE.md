# Contexte Projet — HealthAI Coach (MSPR TPRE501)

## Rôle
Tu es un expert Senior en Data Engineering et Architecture logicielle.
Tu m'aides à finaliser le backend métier d'une startup de santé connectée dans le cadre d'un examen (MSPR).
Approche industrielle : code propre, justifications techniques, Docker, bonnes pratiques.

---

## Stack technique
| Brique | Techno |
|---|---|
| API REST | Python / FastAPI |
| Base de données | PostgreSQL 16 |
| ORM | SQLAlchemy |
| ETL | Python / Pandas |
| Dashboard | Metabase |
| Frontend | React / Vite |
| Conteneurisation | Docker Compose |
| Auth | JWT Bearer Token |

---

## Structure du repo
```
healthAI/
├── services/
│   ├── api/          # FastAPI — Tojo
│   │   ├── main.py
│   │   ├── core/     # config, database, security
│   │   ├── models/   # SQLAlchemy models
│   │   ├── routers/  # endpoints REST
│   │   └── schemas/  # Pydantic schemas
│   ├── etl/          # Pipeline ETL — Houssem
│   │   ├── ingestion.py
│   │   ├── nettoyage.py
│   │   └── run_pipeline.py
│   ├── frontend/     # React/Vite — Hélie
│   └── dashboard/    # Metabase config — Houssem
├── database/
│   └── migrations/
│       └── V1__init_schema.sql   # Migration PostgreSQL
├── docker-compose.yml
└── .env.example
```

---

## Modèle de données (PostgreSQL)
Tables existantes dans `V1__init_schema.sql` :
- `users` — profils utilisateurs + abonnement + rôle
- `nutrition_items` — base nutritionnelle (Daily Food & Nutrition Dataset)
- `exercises` — catalogue d'exercices (ExerciseDB)
- `health_profiles` — données médicales (Diet Recommendations Dataset)
- `user_goals` — objectifs personnalisés
- `user_metrics` — métriques biométriques et d'activité
- `food_logs` — journal alimentaire
- `workout_logs` — journal d'entraînement

Toutes les PKs sont des UUID v4. Timestamps en TIMESTAMPTZ.

---

## Datasets utilisés
| Dataset | Source | Usage |
|---|---|---|
| Daily Food & Nutrition | Kaggle | Base nutritionnelle |
| Diet Recommendations | Kaggle | Profils santé / health_profiles |
| Gym Members Exercise | Kaggle | Profils utilisateurs / biométrie |
| Fitness Tracker | Kaggle | Métriques d'activité quotidienne |
| ExerciseDB | GitHub | Catalogue d'exercices |

---

## État d'avancement

### ✅ Terminé
- `database/migrations/V1__init_schema.sql` — migration PostgreSQL fusionnée et complète
- `services/api/main.py` — bug SessionLocal corrigé, imports propres
- `services/api/models/` — imports relatifs corrigés en absolus (user, nutrition, exercise)
- `services/api/routers/` — imports relatifs corrigés en absolus (auth, users, nutrition, exercises, metrics)
- `docker-compose.yml` — structure complète (postgres, api, etl, frontend, metabase, adminer)

### 🔧 En cours / À faire
- `services/etl/ingestion.py` — chemin Windows hardcodé à remplacer par variable d'environnement
- `services/etl/run_pipeline.py` — étape Load (insertion en BDD) non implémentée
- `docker-compose.yml` — corrections mineures (volume api_venv, healthcheck api)
- `services/api/models/` — modèles health_profile.py et user_goal.py manquants (non bloquant)

---

## Problèmes résolus (à ne pas réintroduire)
1. **Imports relatifs** — tous les `from ..core.`, `from ..models.`, `from ..schemas.` ont été convertis en imports absolus dans models/ et routers/. Ne jamais remettre de `..` dans ces fichiers.
2. **SessionLocal** — doit être importé depuis `core.database` dans `main.py`.
3. **Deux schémas BDD incompatibles** — le dossier `src/` (MySQL/MariaDB de Hanane) est obsolète et ignoré. La seule BDD est PostgreSQL via `database/migrations/`.
4. **metabase_db** — créée à la fin de `V1__init_schema.sql` via `CREATE DATABASE metabase_db`.

---

## Règles de travail
- Toujours utiliser des imports absolus dans `services/api/`
- Ne jamais hardcoder de chemins — utiliser les variables d'environnement (`DATA_DIR`, `DATABASE_URL`)
- Le minimum viable pour l'examen : ETL qui charge 2 datasets en BDD + API qui répond + Metabase qui affiche 1 graphique
- `docker compose up` doit tout démarrer en moins de 30 minutes

---

## Conventions de travail (toutes sessions, tous membres)
1. **Une tâche = une branche dédiée** (`feature/<nom-tache>` ou `fix/<nom-tache>`) depuis `dev`. Jamais de commit direct sur `dev`.
2. **Avant chaque changement de code**, expliquer en 1-2 phrases CE QUE l'on change et POURQUOI, avant de l'exécuter.
3. **Référencer la tâche todo.md** dans les messages de commit (ex : `feat(db): [Phase 1] migration V3 réseau social`).
4. **Pas de push / merge dans `dev` sans diff validé** par Tom (chef de projet).
