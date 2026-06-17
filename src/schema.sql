-- ============================================================
--  HealthAI Coach -- Schema de base de donnees
--  Version : 3.0
--  Moteur   : MariaDB / MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS healthai_coach
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE healthai_coach;

-- 1. users
CREATE TABLE IF NOT EXISTS users (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    email                 VARCHAR(150) NOT NULL UNIQUE,
    age                   TINYINT,
    genre                 ENUM('M','F','autre') DEFAULT 'autre',
    poids_kg              DECIMAL(5,2),
    taille_cm             SMALLINT,
    niveau_fitness        ENUM('debutant','intermediaire','avance') DEFAULT 'debutant',
    water_intake_liters   DECIMAL(4,2),
    workout_frequency     TINYINT,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. biometrics
CREATE TABLE IF NOT EXISTS biometrics (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    date_mesure   DATE NOT NULL,
    poids_kg      DECIMAL(5,2),
    bpm_moyen     SMALLINT,
    bpm_max       SMALLINT,
    bpm_repos     SMALLINT,
    bmi           DECIMAL(4,2),
    body_fat_pct  DECIMAL(4,2),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. foods
CREATE TABLE IF NOT EXISTS foods (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    nom            VARCHAR(200) NOT NULL,
    categorie      VARCHAR(100),
    calories_kcal  DECIMAL(7,2) DEFAULT 0,
    proteines_g    DECIMAL(6,2) DEFAULT 0,
    glucides_g     DECIMAL(6,2) DEFAULT 0,
    lipides_g      DECIMAL(6,2) DEFAULT 0,
    fibres_g       DECIMAL(6,2) DEFAULT 0,
    sucres_g       DECIMAL(6,2) DEFAULT 0,
    sodium_mg      DECIMAL(7,2) DEFAULT 0,
    cholesterol_mg DECIMAL(7,2) DEFAULT 0,
    type_repas     VARCHAR(50)  DEFAULT 'collation',
    water_intake_ml DECIMAL(7,2) DEFAULT 0,
    source_donnee  VARCHAR(100),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. exercises
CREATE TABLE IF NOT EXISTS exercises (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nom           VARCHAR(150) NOT NULL UNIQUE,
    type_exercice VARCHAR(50),
    muscle_cible  VARCHAR(100),
    equipement    VARCHAR(100),
    niveau        ENUM('debutant','intermediaire','avance') DEFAULT 'intermediaire',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. health_profiles  (données médicales issues de diet_recommendations_bdd)
CREATE TABLE IF NOT EXISTS health_profiles (
    id                              INT AUTO_INCREMENT PRIMARY KEY,
    user_id                         INT NOT NULL,
    disease_type                    VARCHAR(100),
    severity                        ENUM('Mild','Moderate','Severe') DEFAULT 'Mild',
    physical_activity_level         ENUM('Low','Moderate','High') DEFAULT 'Moderate',
    cholesterol_mg_dl               DECIMAL(6,2),
    blood_pressure_mmhg             SMALLINT,
    glucose_mg_dl                   DECIMAL(6,2),
    dietary_restrictions            VARCHAR(200),
    allergies                       VARCHAR(200),
    preferred_cuisine               VARCHAR(100),
    weekly_exercise_hours           DECIMAL(4,1),
    adherence_to_diet_plan          DECIMAL(5,2),
    dietary_nutrient_imbalance_score DECIMAL(4,2),
    diet_recommendation             VARCHAR(100),
    created_at                      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. user_goals
CREATE TABLE IF NOT EXISTS user_goals (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    type_objectif ENUM('perte_poids','prise_masse','maintien','sommeil','equilibre') DEFAULT 'maintien',
    valeur_cible  DECIMAL(7,2),
    date_debut    DATE,
    date_fin      DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. activity_logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL,
    exercise_id      INT,
    date_seance      DATE NOT NULL,
    duree_min        SMALLINT,
    calories_brulees DECIMAL(7,2),
    FOREIGN KEY (user_id)     REFERENCES users(id)     ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. nutrition_logs
CREATE TABLE IF NOT EXISTS nutrition_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    food_id    INT,
    date_repas DATE NOT NULL,
    repas      ENUM('petit_dejeuner','dejeuner','diner','collation') DEFAULT 'collation',
    quantite_g DECIMAL(6,2) DEFAULT 150.00,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
