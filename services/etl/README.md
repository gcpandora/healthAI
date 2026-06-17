# ETL Pipeline — HealthAI Coach

Pipeline Extract → Transform → Load pour alimenter PostgreSQL avec les datasets de santé.

---

## 📦 Architecture

```
services/etl/
├── pipelines/
│   ├── ingestion.py      # Étape 1 : Lecture et inventaire des sources
│   ├── nettoyage_v2.py   # Étape 2 : Transformation et nettoyage
│   ├── load.py           # Étape 3 : Insertion en PostgreSQL
│   └── run_pipeline.py   # Orchestrateur principal
├── data/
│   ├── raw/              # Datasets Kaggle bruts (non committé)
│   ├── clean_bdd/        # Datasets nettoyés pour la BDD
│   └── clean_ml/         # Datasets nettoyés pour ML
└── rapport/              # Rapports générés (inventaire, nettoyage)
```

---

## 🚀 Setup des datasets

### ⚡ Option A : Script automatisé (recommandé)

```bash
cd services/etl
python setup_datasets.py
```

Ce script :
- ✅ Crée les dossiers `data/raw/`, `data/clean_bdd/`, `data/clean_ml/`
- ✅ Vérifie les datasets téléchargés et décompresse les ZIP si besoin
- ✅ Génère un rapport de vérification

### 📥 Option B : Télécharger manuellement depuis Kaggle

1. **Créer un compte Kaggle** : https://www.kaggle.com

2. **Configurer l'API Kaggle** :
   ```bash
   # Installer kaggle
   pip install kaggle
   
   # Télécharger la clé API depuis https://www.kaggle.com/settings/account
   # La placer dans ~/.kaggle/kaggle.json (Unix/Mac)
   # ou C:\Users\<USERNAME>\.kaggle\kaggle.json (Windows)
   ```

3. **Télécharger les datasets** :
   ```bash
   mkdir -p services/etl/data/raw
   
   # Daily Food & Nutrition Dataset
   kaggle datasets download -d sootersaalu/daily-nutrition
   unzip daily-nutrition.zip -d services/etl/data/raw
   
   # Diet Recommendations Dataset
   kaggle datasets download -d timmofeyp/diet
   unzip diet.zip -d services/etl/data/raw
   
   # Gym Members Exercise Tracking
   kaggle datasets download -d niharika41298/gym-members-exercise-dataset
   unzip gym-members-exercise-dataset.zip -d services/etl/data/raw
   ```

4. **Vérifier les fichiers** :
   ```bash
   ls -la services/etl/data/raw/
   # daily_food_nutrition_dataset.csv
   # diet_recommendations_dataset.csv
   # gym_members_exercise_tracking.csv
   # gym_members_exercise_tracking_synthetic_data.csv
   ```

---

## 🔄 Exécuter le pipeline

### Depuis Docker (production)
```bash
docker compose up etl
```

### Localement (développement)

1. **Installer les dépendances** :
   ```bash
   cd services/etl
   pip install -r requirements.txt
   ```

2. **Configurer les variables d'environnement** :
   ```bash
   cp ../../.env.example .env
   # Éditer .env avec vos chemins locaux
   ```

3. **Lancer le pipeline** :
   ```bash
   python pipelines/run_pipeline.py
   ```

---

## 📊 Étapes du pipeline

### 1️⃣ **Extract** (`ingestion.py`)
- Lit les 4 datasets Kaggle bruts
- Génère `rapport_inventaire.md` (nombre de lignes, colonnes, doublons, NaN)
- ✅ **Output** : `rapport/rapport_inventaire.md`

### 2️⃣ **Transform** (`nettoyage_v2.py`)
- Nettoyage : suppression de doublons, gestion des valeurs manquantes
- Séparation en 2 outputs :
  - `data/clean_bdd/` : données validées pour PostgreSQL
  - `data/clean_ml/` : données préparées pour ML/Analytics
- ✅ **Output** : `rapport/rapport_nettoyage_v2.md`

### 3️⃣ **Load** (`load.py`)
- Insère les données nettoyées dans PostgreSQL
- Tables cibles :
  - `nutrition_items` ← `daily_food_nutrition_bdd.csv`
  - `users`, `user_metrics` ← `gym_members_exercise_bdd.csv`
  - `health_profiles` ← `diet_recommendations_bdd.csv`
- Gère les conflits (doublons) avec `ON CONFLICT DO NOTHING`
- ✅ **Output** : Logs dans `rapport/pipeline.log`

---

## 🔐 Variables d'environnement

```bash
# Chemins des données (defaults = chemins Docker)
DATA_DIR=/app/data/raw              # Où lire les datasets bruts
BDD_DIR=/app/data/clean_bdd         # Où écrire les datasets nettoyés
ML_DIR=/app/data/clean_ml           # Où écrire les données ML
RAPPORT_DIR=/app/rapport            # Où écrire les rapports

# Connexion PostgreSQL
DATABASE_URL=postgresql://healthai_user:password@postgres:5432/healthai_db
```

À ajouter dans `.env` à la racine du projet.

---

## ✅ Checklist de validation

Après chaque exécution du pipeline, vérifier :

```bash
# 1. Rapports générés
ls -la rapport/
# rapport_inventaire.md
# rapport_nettoyage_v2.md
# pipeline.log

# 2. Données nettoyées
ls -la data/clean_bdd/
# daily_food_nutrition_bdd.csv
# gym_members_exercise_bdd.csv
# diet_recommendations_bdd.csv

# 3. Contenu BDD (en SQL)
psql postgresql://healthai_user:password@postgres:5432/healthai_db -c \
  "SELECT COUNT(*) as nutrition_count FROM nutrition_items;"
```

---

## 🐛 Troubleshooting

### Erreur : "FileNotFoundError: daily_food_nutrition_dataset.csv"
→ Télécharger les datasets avec l'Option A ou B ci-dessous.

### Erreur : "ModuleNotFoundError: No module named 'pandas'"
→ `pip install -r requirements.txt`

### Erreur : "could not connect to server"
→ PostgreSQL n'est pas démarré. Lancer `docker compose up postgres`.

### Erreur : "ON CONFLICT" ou contrainte unique
→ L'ETL peut être relancé plusieurs fois, les doublons sont ignorés.

---

## 📚 Ressources

| Dataset | Source | Size |
|---------|--------|------|
| Daily Food & Nutrition | Kaggle | ~1 MB |
| Diet Recommendations | Kaggle | ~0.5 MB |
| Gym Members Exercise | Kaggle | ~2 MB |

---

**Pour l'équipe dataviz** : Après exécution du pipeline, les données sont disponibles dans PostgreSQL. Interroger directement la BDD depuis Metabase/Frontend, pas les CSV. ✅
