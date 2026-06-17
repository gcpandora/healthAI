-- ════════════════════════════════════════════════════════════════
-- HealthAI Coach — Migration initiale (v2 — fusionnée)
-- Fichier  : V1__init_schema.sql
-- Moteur   : PostgreSQL 16
-- Auteurs  : Hanane (modèle métier) + Tojo (structure PostgreSQL)
-- Fusion   : Tom (DevOps)
--
-- Ce script est exécuté automatiquement au premier démarrage
-- du container PostgreSQL via docker-entrypoint-initdb.d
--
-- Choix techniques justifiés :
--   - UUID v4 comme PK  → évite les collisions en environnement distribué
--   - TIMESTAMPTZ       → stockage UTC, affiché dans le fuseau client
--   - CHECK constraints → validation côté BDD (filet de sécurité ETL)
--   - ON DELETE CASCADE → cohérence référentielle sans orphelins
-- ════════════════════════════════════════════════════════════════

-- Extension UUID (disponible nativement dans PostgreSQL 13+)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ─────────────────────────────────────────────────────────────────
-- TABLE : users
-- Source : Gym Members Exercise Dataset + Diet Recommendations
-- Champs démographiques + objectif + abonnement + rôle
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    username      VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    -- Données démographiques (issues Gym Members Dataset)
    age           INTEGER       CHECK (age > 0 AND age < 120),
    gender        VARCHAR(10)   CHECK (gender IN ('male', 'female', 'other')),
    height_cm     NUMERIC(5,2)  CHECK (height_cm > 0),
    weight_kg     NUMERIC(5,2)  CHECK (weight_kg > 0),

    -- Activité de base (issues Fitness Tracker Dataset)
    water_intake_liters  NUMERIC(4,2),
    workout_frequency    SMALLINT,        -- séances/semaine

    -- Objectif personnel
    goal          VARCHAR(50)   CHECK (goal IN (
                      'weight_loss', 'muscle_gain',
                      'sleep_improvement', 'maintenance', 'general_health'
                  )),

    -- Niveau fitness
    fitness_level VARCHAR(20)   CHECK (fitness_level IN (
                      'beginner', 'intermediate', 'advanced'
                  )) DEFAULT 'beginner',

    -- Abonnement (business model HealthAI Coach)
    plan          VARCHAR(20)   DEFAULT 'free' CHECK (plan IN (
                      'free', 'premium', 'premium_plus'
                  )),

    -- Rôle applicatif
    role          VARCHAR(20)   DEFAULT 'user' CHECK (role IN ('user', 'admin')),

    created_at    TIMESTAMPTZ   DEFAULT NOW(),
    updated_at    TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email      ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : nutrition_items
-- Source : Daily Food & Nutrition Dataset (Kaggle)
-- Base nutritionnelle de référence — enrichie des champs Hanane
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS nutrition_items (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(255) NOT NULL,
    category      VARCHAR(100),
    meal_type     VARCHAR(50)  CHECK (meal_type IN (
                      'breakfast', 'lunch', 'dinner', 'snack'
                  )),

    -- Macronutriments (pour 100g — standard nutritionnel)
    calories      NUMERIC(7,2) DEFAULT 0,
    proteins_g    NUMERIC(7,2) DEFAULT 0,
    carbs_g       NUMERIC(7,2) DEFAULT 0,
    fats_g        NUMERIC(7,2) DEFAULT 0,
    fiber_g       NUMERIC(7,2) DEFAULT 0,

    -- Micronutriments (présents dans le dataset Kaggle)
    sugar_g       NUMERIC(7,2) DEFAULT 0,
    sodium_mg     NUMERIC(7,2) DEFAULT 0,
    cholesterol_mg NUMERIC(7,2) DEFAULT 0,
    water_ml      NUMERIC(7,2) DEFAULT 0,

    -- Traçabilité de la source
    source        VARCHAR(100),   -- ex: 'Kaggle - Daily Food & Nutrition'
    created_at    TIMESTAMPTZ     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nutrition_name     ON nutrition_items(name);
CREATE INDEX IF NOT EXISTS idx_nutrition_category ON nutrition_items(category);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : exercises
-- Source : ExerciseDB API / GitHub Repository
-- Catalogue d'exercices avec métadonnées complètes
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS exercises (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(255) NOT NULL UNIQUE,
    type          VARCHAR(50),             -- cardio, strength, flexibility, etc.
    muscle_group  VARCHAR(100),            -- chest, legs, core, etc.
    equipment     VARCHAR(100),            -- dumbbell, barbell, bodyweight, etc.
    difficulty    VARCHAR(20)  CHECK (difficulty IN (
                      'beginner', 'intermediate', 'advanced'
                  )) DEFAULT 'intermediate',
    instructions  TEXT,

    -- Référence vers la source ExerciseDB
    external_id   VARCHAR(100),            -- ID dans l'API ExerciseDB
    source        VARCHAR(100),

    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exercises_type       ON exercises(type);
CREATE INDEX IF NOT EXISTS idx_exercises_difficulty ON exercises(difficulty);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : health_profiles  ← ajout Hanane (absent du V1 IA)
-- Source : Diet Recommendations Dataset (Kaggle)
-- Données médicales et diététiques par utilisateur
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS health_profiles (
    id                              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Profil médical (issu Diet Recommendations Dataset)
    disease_type                    VARCHAR(100),
    severity                        VARCHAR(10)  CHECK (severity IN ('mild', 'moderate', 'severe')),
    physical_activity_level         VARCHAR(10)  CHECK (physical_activity_level IN ('low', 'moderate', 'high')),
    cholesterol_mg_dl               NUMERIC(6,2),
    blood_pressure_mmhg             SMALLINT,
    glucose_mg_dl                   NUMERIC(6,2),

    -- Préférences alimentaires
    dietary_restrictions            VARCHAR(200),
    allergies                       VARCHAR(200),
    preferred_cuisine               VARCHAR(100),

    -- Métriques de suivi
    weekly_exercise_hours           NUMERIC(4,1),
    adherence_to_diet_plan          NUMERIC(5,2),   -- % d'adhérence
    dietary_nutrient_imbalance_score NUMERIC(4,2),

    -- Recommandation générée
    diet_recommendation             VARCHAR(100),

    created_at                      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_profiles_user_id ON health_profiles(user_id);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : user_goals  ← ajout Hanane (absent du V1 IA)
-- Objectifs personnalisés et traçabilité de leur évolution
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_goals (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    goal_type     VARCHAR(50)  CHECK (goal_type IN (
                      'weight_loss', 'muscle_gain', 'maintenance',
                      'sleep_improvement', 'general_health'
                  )),
    target_value  NUMERIC(7,2),            -- ex: 70.00 pour poids cible en kg
    start_date    DATE,
    end_date      DATE,

    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_goals_user_id ON user_goals(user_id);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : user_metrics
-- Source : Gym Members Exercise Dataset + Fitness Tracker Dataset
-- Métriques biométriques et d'activité dans le temps
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_metrics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Biométrie (Gym Members Dataset)
    weight_kg       NUMERIC(5,2),
    body_fat_pct    NUMERIC(5,2),
    bmi             NUMERIC(5,2),
    heart_rate_avg  INTEGER,
    heart_rate_max  INTEGER,
    heart_rate_rest INTEGER,    -- ajout Hanane : bpm_repos

    -- Activité quotidienne (Fitness Tracker Dataset)
    steps           INTEGER,
    active_minutes  INTEGER,
    calories_burned NUMERIC(7,2),

    -- Sommeil
    sleep_hours     NUMERIC(4,2)
);

CREATE INDEX IF NOT EXISTS idx_user_metrics_user_id     ON user_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_metrics_recorded_at ON user_metrics(recorded_at);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : food_logs
-- Journal alimentaire quotidien des utilisateurs
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS food_logs (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nutrition_item_id UUID NOT NULL REFERENCES nutrition_items(id) ON DELETE RESTRICT,

    quantity_g        NUMERIC(7,2) NOT NULL CHECK (quantity_g > 0),
    meal_type         VARCHAR(20)  CHECK (meal_type IN (
                          'breakfast', 'lunch', 'dinner', 'snack'
                      )),
    logged_at         TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_food_logs_user_id   ON food_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_food_logs_logged_at ON food_logs(logged_at);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : workout_logs
-- Journal d'entraînement des utilisateurs
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workout_logs (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id  UUID NOT NULL REFERENCES exercises(id) ON DELETE RESTRICT,

    duration_min INTEGER      CHECK (duration_min > 0),
    sets         INTEGER,
    reps         INTEGER,
    calories_burned NUMERIC(7,2),   -- ajout Hanane : calories_brulees
    logged_at    TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workout_logs_user_id   ON workout_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_logs_logged_at ON workout_logs(logged_at);


-- ─────────────────────────────────────────────────────────────────
-- TRIGGER : mise à jour automatique de updated_at sur users
-- ─────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ─────────────────────────────────────────────────────────────────
-- BASE METABASE (dashboard analytique)
-- Doit être créée dans le même script pour que le container
-- Metabase puisse s'y connecter dès le premier démarrage
-- ─────────────────────────────────────────────────────────────────
CREATE DATABASE metabase_db;
