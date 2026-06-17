
import os
import uuid
import random
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger

# ── Connexion BDD ───────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://healthai_user:password@postgres:5432/healthai_db"
)
BDD_DIR = os.getenv("BDD_DIR", "/app/data/clean_bdd")

engine = create_engine(DATABASE_URL, future=True)


# ══════════════════════════════════════════════════════════════════
# NUTRITION ITEMS
# ══════════════════════════════════════════════════════════════════
def load_nutrition_items() -> int:
    """
    Charge daily_food_nutrition_bdd.csv dans la table nutrition_items.
    Ignore les doublons sur le nom (ON CONFLICT DO NOTHING).
    """
    path = os.path.join(BDD_DIR, "daily_food_nutrition_bdd.csv")
    if not os.path.exists(path):
        logger.warning(f"⚠️  Fichier introuvable : {path}")
        return 0

    df = pd.read_csv(path)
    logger.info(f"   📄 {len(df)} lignes à charger dans nutrition_items")

    # Mapping colonnes CSV → colonnes BDD (gère les variations de noms)
    col_map = {
        "food_item":       "name",
        "food":            "name",
        "calories_kcal":   "calories",
        "protein_g":       "proteins_g",
        "carbohydrates_g": "carbs_g",
        "fat_g":           "fats_g",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    if "name" not in df.columns:
        logger.error("❌ Colonne 'name' introuvable dans le CSV nutrition")
        return 0

    target_cols = [
        "name", "category", "meal_type",
        "calories", "proteins_g", "carbs_g", "fats_g", "fiber_g",
        "sugar_g", "sodium_mg", "cholesterol_mg", "water_ml",
    ]
    available = [c for c in target_cols if c in df.columns]
    df = df[available].copy()
    df["source"] = "Kaggle - Daily Food & Nutrition Dataset"
    df = df.dropna(subset=["name"])
    df = df.drop_duplicates(subset=["name"])

    valid_meals = {"breakfast", "lunch", "dinner", "snack"}

    loaded = 0
    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                meal_raw = str(row.get("meal_type", "")).strip().lower() if pd.notna(row.get("meal_type")) else None

                conn.execute(text("""
                    INSERT INTO nutrition_items (
                        id, name, category, meal_type,
                        calories, proteins_g, carbs_g, fats_g, fiber_g,
                        sugar_g, sodium_mg, cholesterol_mg, water_ml, source
                    ) VALUES (
                        :id, :name, :category, :meal_type,
                        :calories, :proteins_g, :carbs_g, :fats_g, :fiber_g,
                        :sugar_g, :sodium_mg, :cholesterol_mg, :water_ml, :source
                    ) ON CONFLICT DO NOTHING
                """), {
                    "id":             str(uuid.uuid4()),
                    "name":           str(row.get("name", ""))[:255],
                    "category":       str(row["category"])[:100]      if pd.notna(row.get("category"))       else None,
                    "meal_type":      meal_raw                         if meal_raw in valid_meals             else None,
                    "calories":       float(row["calories"])           if pd.notna(row.get("calories"))       else 0,
                    "proteins_g":     float(row["proteins_g"])         if pd.notna(row.get("proteins_g"))     else 0,
                    "carbs_g":        float(row["carbs_g"])            if pd.notna(row.get("carbs_g"))        else 0,
                    "fats_g":         float(row["fats_g"])             if pd.notna(row.get("fats_g"))         else 0,
                    "fiber_g":        float(row["fiber_g"])            if pd.notna(row.get("fiber_g"))        else 0,
                    "sugar_g":        float(row["sugar_g"])            if pd.notna(row.get("sugar_g"))        else 0,
                    "sodium_mg":      float(row["sodium_mg"])          if pd.notna(row.get("sodium_mg"))      else 0,
                    "cholesterol_mg": float(row["cholesterol_mg"])     if pd.notna(row.get("cholesterol_mg")) else 0,
                    "water_ml":       float(row["water_ml"])           if pd.notna(row.get("water_ml"))       else 0,
                    "source":         "Kaggle - Daily Food & Nutrition Dataset",
                })
                loaded += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Ligne ignorée nutrition : {e}")
        conn.commit()

    logger.success(f"   ✅ {loaded} aliments chargés dans nutrition_items")
    return loaded


# ══════════════════════════════════════════════════════════════════
# USERS + USER_METRICS
# ══════════════════════════════════════════════════════════════════
def _load_gym_file(path: str) -> int:
    """
    Charge un fichier gym (exercise ou synthetic) dans users + user_metrics.
    Factorisation commune aux deux datasets gym.
    """
    if not os.path.exists(path):
        logger.warning(f"⚠️  Fichier introuvable : {path}")
        return 0

    df = pd.read_csv(path)
    logger.info(f"   📄 {len(df)} lignes à charger depuis {os.path.basename(path)}")

    level_map = {1: "beginner", 2: "intermediate", 3: "advanced"}
    valid_goals = {"weight_loss", "muscle_gain", "sleep_improvement", "maintenance", "general_health"}

    loaded = 0
    with engine.connect() as conn:
        for i, row in df.iterrows():
            user_id = str(uuid.uuid4())
            try:
                # Genre
                gender_raw = str(row.get("gender", "")).strip().lower()
                gender = (
                    "male"   if gender_raw in {"male", "m", "homme"} else
                    "female" if gender_raw in {"female", "f", "femme"} else
                    "other"
                )

                # Niveau fitness depuis experience_level (1/2/3)
                exp = row.get("experience_level", 1)
                fitness_level = level_map.get(int(exp) if pd.notna(exp) else 1, "beginner")

                # Workout frequency — plusieurs noms de colonnes possibles
                wf_col = next((c for c in ["workout_frequency_days_week",
                                            "workout_frequency_days/week",
                                            "workout_frequency"] if c in df.columns), None)
                workout_freq = int(row[wf_col]) if wf_col and pd.notna(row.get(wf_col)) else None

                # Height : convertir m → cm si colonne height_m
                if "height_m" in df.columns:
                    height_cm = float(row["height_m"]) * 100 if pd.notna(row.get("height_m")) else None
                elif "height_cm" in df.columns:
                    height_cm = float(row["height_cm"]) if pd.notna(row.get("height_cm")) else None
                else:
                    height_cm = None

                # Insérer utilisateur
                conn.execute(text("""
                    INSERT INTO users (
                        id, email, username, password_hash,
                        age, gender, height_cm, weight_kg,
                        fitness_level, water_intake_liters, workout_frequency,
                        goal, plan, role
                    ) VALUES (
                        :id, :email, :username, :password_hash,
                        :age, :gender, :height_cm, :weight_kg,
                        :fitness_level, :water_intake_liters, :workout_frequency,
                        :goal, :plan, :role
                    ) ON CONFLICT DO NOTHING
                """), {
                    "id":                  user_id,
                    "email":               f"user_{i}_{user_id[:8]}@healthai.local",
                    "username":            f"user_{i}",
                    "password_hash":       "etl_import_no_login",
                    "age":                 int(row["age"])               if pd.notna(row.get("age"))               else None,
                    "gender":              gender,
                    "height_cm":           height_cm,
                    "weight_kg":           float(row["weight_kg"])        if pd.notna(row.get("weight_kg"))        else None,
                    "fitness_level":       fitness_level,
                    "water_intake_liters": float(row["water_intake_liters"]) if pd.notna(row.get("water_intake_liters")) else None,
                    "workout_frequency":   workout_freq,
                    "goal":                "general_health",
                    "plan":                "free",
                    "role":                "user",
                })

                # Insérer métriques biométriques
                conn.execute(text("""
                    INSERT INTO user_metrics (
                        id, user_id,
                        weight_kg, bmi, body_fat_pct,
                        heart_rate_avg, heart_rate_max, heart_rate_rest,
                        calories_burned
                    ) VALUES (
                        :id, :user_id,
                        :weight_kg, :bmi, :body_fat_pct,
                        :heart_rate_avg, :heart_rate_max, :heart_rate_rest,
                        :calories_burned
                    )
                """), {
                    "id":              str(uuid.uuid4()),
                    "user_id":         user_id,
                    "weight_kg":       float(row["weight_kg"])       if pd.notna(row.get("weight_kg"))       else None,
                    "bmi":             float(row["bmi"])              if pd.notna(row.get("bmi"))              else None,
                    "body_fat_pct":    float(row["fat_percentage"])   if pd.notna(row.get("fat_percentage"))   else None,
                    "heart_rate_avg":  int(row["avg_bpm"])            if pd.notna(row.get("avg_bpm"))          else None,
                    "heart_rate_max":  int(row["max_bpm"])            if pd.notna(row.get("max_bpm"))          else None,
                    "heart_rate_rest": int(row["resting_bpm"])        if pd.notna(row.get("resting_bpm"))      else None,
                    "calories_burned": float(row["calories_burned"])  if pd.notna(row.get("calories_burned"))  else None,
                })

                loaded += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Ligne {i} ignorée gym : {e}")

        conn.commit()

    return loaded


def load_users_and_metrics() -> int:
    """
    Charge gym_members_exercise_bdd.csv et gym_members_synthetic_bdd.csv
    dans les tables users + user_metrics.
    """
    n1 = _load_gym_file(os.path.join(BDD_DIR, "gym_members_exercise_bdd.csv"))
    logger.success(f"   ✅ {n1} utilisateurs (gym exercise) chargés")

    n2 = _load_gym_file(os.path.join(BDD_DIR, "gym_members_synthetic_bdd.csv"))
    logger.success(f"   ✅ {n2} utilisateurs (gym synthetic) chargés")

    return n1 + n2


# ══════════════════════════════════════════════════════════════════
# HEALTH PROFILES
# ══════════════════════════════════════════════════════════════════
def load_health_profiles() -> int:
    """
    Charge diet_recommendations_bdd.csv dans la table health_profiles.
    Chaque profil est lié à un utilisateur existant (chargé par load_users_and_metrics).
    La liaison se fait par index cyclique : profil i → users[i % nb_users].
    """
    path = os.path.join(BDD_DIR, "diet_recommendations_bdd.csv")
    if not os.path.exists(path):
        logger.warning(f"⚠️  Fichier introuvable : {path}")
        return 0

    df = pd.read_csv(path)
    logger.info(f"   📄 {len(df)} lignes à charger dans health_profiles")

    # Récupérer les IDs des utilisateurs ETL (role=user, par ordre de création)
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT id FROM users WHERE role = 'user' ORDER BY created_at ASC"
        ))
        user_ids = [str(row[0]) for row in result]

    if not user_ids:
        logger.warning("⚠️  Aucun utilisateur en BDD — health_profiles non chargés. Lancer load_users_and_metrics() d'abord.")
        return 0

    valid_severity = {"mild", "moderate", "severe"}
    valid_activity = {"low", "moderate", "high"}

    loaded = 0
    with engine.connect() as conn:
        for i, row in df.iterrows():
            try:
                user_id = user_ids[i % len(user_ids)]

                severity = str(row.get("severity", "")).strip().lower() if pd.notna(row.get("severity")) else None
                activity = str(row.get("physical_activity_level", "")).strip().lower() if pd.notna(row.get("physical_activity_level")) else None

                conn.execute(text("""
                    INSERT INTO health_profiles (
                        id, user_id,
                        disease_type, severity, physical_activity_level,
                        cholesterol_mg_dl, blood_pressure_mmhg, glucose_mg_dl,
                        dietary_restrictions, allergies, preferred_cuisine,
                        weekly_exercise_hours, adherence_to_diet_plan,
                        dietary_nutrient_imbalance_score, diet_recommendation
                    ) VALUES (
                        :id, :user_id,
                        :disease_type, :severity, :physical_activity_level,
                        :cholesterol_mg_dl, :blood_pressure_mmhg, :glucose_mg_dl,
                        :dietary_restrictions, :allergies, :preferred_cuisine,
                        :weekly_exercise_hours, :adherence_to_diet_plan,
                        :dietary_nutrient_imbalance_score, :diet_recommendation
                    ) ON CONFLICT DO NOTHING
                """), {
                    "id":                              str(uuid.uuid4()),
                    "user_id":                         user_id,
                    "disease_type":                    str(row["disease_type"])[:100]            if pd.notna(row.get("disease_type"))                    else None,
                    "severity":                        severity                                   if severity in valid_severity                           else None,
                    "physical_activity_level":         activity                                   if activity in valid_activity                           else None,
                    "cholesterol_mg_dl":               float(row["cholesterol_mg_dl"])            if pd.notna(row.get("cholesterol_mg_dl"))               else None,
                    "blood_pressure_mmhg":             int(row["blood_pressure_mmhg"])            if pd.notna(row.get("blood_pressure_mmhg"))             else None,
                    "glucose_mg_dl":                   float(row["glucose_mg_dl"])                if pd.notna(row.get("glucose_mg_dl"))                   else None,
                    "dietary_restrictions":            str(row["dietary_restrictions"])[:200]     if pd.notna(row.get("dietary_restrictions"))            else None,
                    "allergies":                       str(row["allergies"])[:200]                if pd.notna(row.get("allergies"))                       else None,
                    "preferred_cuisine":               str(row["preferred_cuisine"])[:100]        if pd.notna(row.get("preferred_cuisine"))               else None,
                    "weekly_exercise_hours":           float(row["weekly_exercise_hours"])        if pd.notna(row.get("weekly_exercise_hours"))           else None,
                    "adherence_to_diet_plan":          float(row["adherence_to_diet_plan"])       if pd.notna(row.get("adherence_to_diet_plan"))          else None,
                    "dietary_nutrient_imbalance_score":float(row["dietary_nutrient_imbalance_score"]) if pd.notna(row.get("dietary_nutrient_imbalance_score")) else None,
                    "diet_recommendation":             str(row["diet_recommendation"])[:100]      if pd.notna(row.get("diet_recommendation"))             else None,
                })
                loaded += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Ligne {i} ignorée health_profile : {e}")

        conn.commit()

    logger.success(f"   ✅ {loaded} profils de santé chargés dans health_profiles")
    return loaded


# ══════════════════════════════════════════════════════════════════
# EXERCISES (simulé)
# ══════════════════════════════════════════════════════════════════
def load_exercises() -> int:
    """
    Insère un catalogue simulé d'exercices dans la table exercises.
    Couvre les 3 niveaux (beginner/intermediate/advanced),
    les principaux types (cardio/strength/flexibility/balance)
    et les groupes musculaires du schéma.
    Ignore les doublons sur le nom (ON CONFLICT DO NOTHING).
    """

    EXERCISES = [
        # ── Cardio ─────────────────────────────────────────────
        ("Running",            "cardio",      "full body",   "none",         "beginner",     "Run at a steady pace for the desired duration."),
        ("Cycling",            "cardio",      "legs",        "bike",         "beginner",     "Pedal at a consistent cadence, adjusting resistance as needed."),
        ("Jump Rope",          "cardio",      "full body",   "jump rope",    "beginner",     "Jump continuously, keeping a steady rhythm."),
        ("Rowing Machine",     "cardio",      "full body",   "rowing machine","intermediate","Drive with legs, lean back, then pull the handle to your chest."),
        ("HIIT Sprint",        "cardio",      "full body",   "none",         "advanced",     "Alternate 30s max-effort sprints with 30s rest for 10 rounds."),
        ("Stair Climbing",     "cardio",      "legs",        "none",         "beginner",     "Climb stairs at a steady pace, keeping your back straight."),
        ("Swimming",           "cardio",      "full body",   "pool",         "intermediate", "Maintain proper form throughout each stroke."),
        ("Elliptical Trainer", "cardio",      "full body",   "elliptical",   "beginner",     "Maintain a smooth motion, keeping your core engaged."),

        # ── Strength — Chest ───────────────────────────────────
        ("Push-Up",            "strength",    "chest",       "none",         "beginner",     "Keep body straight, lower chest to floor, push back up."),
        ("Bench Press",        "strength",    "chest",       "barbell",      "intermediate", "Lower bar to chest, press upward until arms are fully extended."),
        ("Incline Dumbbell Press","strength", "chest",       "dumbbell",     "intermediate", "Press dumbbells upward from an inclined bench position."),
        ("Cable Fly",          "strength",    "chest",       "cable machine","advanced",     "Bring cables together in a wide arc, squeezing chest at peak."),
        ("Dips",               "strength",    "chest",       "dip bar",      "intermediate", "Lower body until upper arms are parallel to floor, then push up."),

        # ── Strength — Back ────────────────────────────────────
        ("Pull-Up",            "strength",    "back",        "pull-up bar",  "intermediate", "Hang from bar, pull chin above bar, lower with control."),
        ("Barbell Row",        "strength",    "back",        "barbell",      "intermediate", "Hinge at hips, pull bar to lower chest, keep back flat."),
        ("Lat Pulldown",       "strength",    "back",        "cable machine","beginner",     "Pull bar to upper chest, elbows pointing down."),
        ("Deadlift",           "strength",    "back",        "barbell",      "advanced",     "Hinge at hips, keep back neutral, drive hips forward to stand."),
        ("Seated Cable Row",   "strength",    "back",        "cable machine","beginner",     "Pull handle to abdomen, keeping torso upright."),

        # ── Strength — Legs ────────────────────────────────────
        ("Squat",              "strength",    "legs",        "barbell",      "beginner",     "Feet shoulder-width apart, lower until thighs are parallel, drive up."),
        ("Leg Press",          "strength",    "legs",        "machine",      "beginner",     "Push platform away until legs are extended, lower with control."),
        ("Romanian Deadlift",  "strength",    "legs",        "barbell",      "intermediate", "Hinge at hips with slight knee bend, lower bar along shins."),
        ("Lunges",             "strength",    "legs",        "dumbbell",     "beginner",     "Step forward, lower back knee toward floor, return to start."),
        ("Leg Curl",           "strength",    "legs",        "machine",      "beginner",     "Curl legs toward glutes, hold briefly, lower with control."),
        ("Calf Raises",        "strength",    "legs",        "none",         "beginner",     "Rise onto toes, hold at peak, lower slowly."),
        ("Bulgarian Split Squat","strength",  "legs",        "dumbbell",     "advanced",     "Rear foot elevated, lower front knee to 90°, drive back up."),

        # ── Strength — Shoulders ──────────────────────────────
        ("Overhead Press",     "strength",    "shoulders",   "barbell",      "intermediate", "Press bar from shoulders to overhead, keep core braced."),
        ("Lateral Raise",      "strength",    "shoulders",   "dumbbell",     "beginner",     "Raise arms to sides until parallel to floor, lower slowly."),
        ("Face Pull",          "strength",    "shoulders",   "cable machine","beginner",     "Pull rope to face level, flare elbows out."),

        # ── Strength — Arms ────────────────────────────────────
        ("Barbell Curl",       "strength",    "arms",        "barbell",      "beginner",     "Curl bar to shoulder height, squeeze biceps, lower slowly."),
        ("Tricep Pushdown",    "strength",    "arms",        "cable machine","beginner",     "Push bar down until arms are straight, control the return."),
        ("Hammer Curl",        "strength",    "arms",        "dumbbell",     "beginner",     "Curl with neutral grip, keeping elbows fixed."),
        ("Skull Crusher",      "strength",    "arms",        "barbell",      "intermediate", "Lower bar to forehead, extend arms back to start."),

        # ── Strength — Core ────────────────────────────────────
        ("Plank",              "strength",    "core",        "none",         "beginner",     "Hold straight-body position on forearms and toes."),
        ("Crunch",             "strength",    "core",        "none",         "beginner",     "Curl shoulders toward knees, keep lower back on floor."),
        ("Russian Twist",      "strength",    "core",        "none",         "intermediate", "Rotate torso side to side, keeping feet off floor."),
        ("Hanging Leg Raise",  "strength",    "core",        "pull-up bar",  "advanced",     "Hang from bar, raise straight legs to 90°, lower slowly."),
        ("Cable Crunch",       "strength",    "core",        "cable machine","intermediate", "Kneel and crunch downward pulling cable, squeeze abs at bottom."),

        # ── Flexibility ───────────────────────────────────────
        ("Hip Flexor Stretch", "flexibility", "legs",        "none",         "beginner",     "Lunge forward, lower back knee, push hips forward and hold."),
        ("Hamstring Stretch",  "flexibility", "legs",        "none",         "beginner",     "Sit on floor, extend one leg, reach toward toes and hold."),
        ("Chest Opener",       "flexibility", "chest",       "none",         "beginner",     "Clasp hands behind back, open chest, hold 30 seconds."),
        ("Child's Pose",       "flexibility", "back",        "none",         "beginner",     "Kneel and extend arms forward on floor, breathe deeply."),
        ("Pigeon Pose",        "flexibility", "legs",        "none",         "intermediate", "From downward dog, bring one knee forward between hands."),
        ("Thoracic Rotation",  "flexibility", "back",        "none",         "beginner",     "Sit cross-legged, rotate upper back left and right."),

        # ── Balance ───────────────────────────────────────────
        ("Single-Leg Deadlift","balance",     "legs",        "dumbbell",     "intermediate", "Hinge forward on one leg while extending the other behind."),
        ("Bosu Ball Squat",    "balance",     "legs",        "bosu ball",    "intermediate", "Perform squat while standing on rounded side of Bosu ball."),
        ("Tree Pose",          "balance",     "full body",   "none",         "beginner",     "Stand on one foot, place other foot on inner thigh, arms overhead."),
        ("Stability Ball Plank","balance",    "core",        "stability ball","advanced",    "Hold plank position with forearms on stability ball."),
    ]

    loaded = 0
    with engine.connect() as conn:
        for (name, ex_type, muscle_group, equipment,
             difficulty, instructions) in EXERCISES:
            try:
                conn.execute(text("""
                    INSERT INTO exercises (
                        id, name, type, muscle_group, equipment,
                        difficulty, instructions, source
                    ) VALUES (
                        :id, :name, :type, :muscle_group, :equipment,
                        :difficulty, :instructions, :source
                    ) ON CONFLICT DO NOTHING
                """), {
                    "id":           str(uuid.uuid4()),
                    "name":         name,
                    "type":         ex_type,
                    "muscle_group": muscle_group,
                    "equipment":    equipment,
                    "difficulty":   difficulty,
                    "instructions": instructions,
                    "source":       "HealthAI - simulated catalogue",
                })
                loaded += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Exercice ignoré ({name}) : {e}")
        conn.commit()

    logger.success(f"   ✅ {loaded} exercices chargés dans exercises")
    return loaded


# ══════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE DIRECT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    logger.info("🗄️  Démarrage du chargement BDD...")
    n1 = load_nutrition_items()
    n2 = load_users_and_metrics()
    n3 = load_health_profiles()
    n4 = load_exercises()
    logger.success(
        f"✅ Load terminé — {n1} aliments | {n2} utilisateurs | "
        f"{n3} profils santé | {n4} exercices insérés"
    )
