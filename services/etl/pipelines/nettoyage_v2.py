
import pandas as pd
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ── Chemins depuis variables d'environnement Docker ────────────
DATA_DIR    = os.getenv("DATA_DIR",    "/app/data/raw")
BDD_DIR     = os.getenv("BDD_DIR",     "/app/data/clean_bdd")
ML_DIR      = os.getenv("ML_DIR",      "/app/data/clean_ml")
RAPPORT_DIR = os.getenv("RAPPORT_DIR", "/app/rapport")

os.makedirs(BDD_DIR,     exist_ok=True)
os.makedirs(ML_DIR,      exist_ok=True)
os.makedirs(RAPPORT_DIR, exist_ok=True)

rapport_path = os.path.join(RAPPORT_DIR, "rapport_nettoyage_v2.md")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les noms de colonnes : minuscules, underscores, sans caractères spéciaux."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[\s\(\)/]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return df


print("📥 Chargement des données brutes...\n")
food = pd.read_csv(os.path.join(DATA_DIR, "daily_food_nutrition_dataset.csv"), on_bad_lines='skip')
diet = pd.read_csv(os.path.join(DATA_DIR, "diet_recommendations_dataset.csv"))
gym  = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking.csv"))
synt = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking_synthetic_data.csv"))

# ══════════════════════════════════════════════════════════════════
# NETTOYAGE BDD
# Objectif : données prêtes pour insertion SQL
# Stratégie : doublons supprimés, types corrigés, NULL conservés
# ══════════════════════════════════════════════════════════════════
print("=" * 55)
print("📦 NETTOYAGE POUR LA BDD")
print("=" * 55)

# ── 1. daily_food_nutrition → nutrition_items ──────────────────
print("\n🧹 [BDD] daily_food_nutrition → nutrition_items...")
food_bdd = food.drop_duplicates()
food_bdd = normalize_columns(food_bdd)

# Renommages explicites pour correspondre au schéma nutrition_items
food_rename = {
    "food_item":       "name",
    "food":            "name",
    "calories_kcal":   "calories",
    "protein_g":       "proteins_g",
    "carbohydrates_g": "carbs_g",
    "fat_g":           "fats_g",
}
food_bdd = food_bdd.rename(columns={k: v for k, v in food_rename.items() if k in food_bdd.columns})
food_bdd.to_csv(os.path.join(BDD_DIR, "daily_food_nutrition_bdd.csv"), index=False)
print(f"   ✅ {len(food_bdd)} lignes — doublons supprimés, NULL conservés")

# ── 2. diet_recommendations → health_profiles ─────────────────
print("🧹 [BDD] diet_recommendations → health_profiles...")
diet_bdd = diet.copy()
diet_bdd = normalize_columns(diet_bdd)

# Renommages explicites pour correspondre au schéma health_profiles
diet_rename = {
    "disease_type":                      "disease_type",
    "severity":                          "severity",
    "physical_activity_level":           "physical_activity_level",
    "cholesterol_level":                 "cholesterol_mg_dl",
    "cholesterol_mg_dl":                 "cholesterol_mg_dl",
    "blood_pressure":                    "blood_pressure_mmhg",
    "blood_pressure_mmhg":               "blood_pressure_mmhg",
    "glucose_level":                     "glucose_mg_dl",
    "glucose_mg_dl":                     "glucose_mg_dl",
    "dietary_restrictions":              "dietary_restrictions",
    "allergies":                         "allergies",
    "preferred_cuisine":                 "preferred_cuisine",
    "weekly_exercise_hours":             "weekly_exercise_hours",
    "adherence_to_diet_plan_%":          "adherence_to_diet_plan",
    "adherence_to_diet_plan":            "adherence_to_diet_plan",
    "dietary_nutrient_imbalance_score":  "dietary_nutrient_imbalance_score",
    "diet_recommendation":               "diet_recommendation",
    "recommended_diet":                  "diet_recommendation",
    "diet_type":                         "diet_recommendation",
}
diet_bdd = diet_bdd.rename(columns={k: v for k, v in diet_rename.items() if k in diet_bdd.columns})

# Normaliser severity → mild/moderate/severe
if "severity" in diet_bdd.columns:
    sev_map = {
        "mild": "mild", "faible": "mild", "low": "mild",
        "moderate": "moderate", "modéré": "moderate", "modere": "moderate", "medium": "moderate",
        "severe": "severe", "sévère": "severe", "severe": "severe", "high": "severe",
    }
    diet_bdd["severity"] = diet_bdd["severity"].str.strip().str.lower().map(sev_map)

# Normaliser physical_activity_level → low/moderate/high
if "physical_activity_level" in diet_bdd.columns:
    act_map = {
        "low": "low", "faible": "low", "sedentary": "low",
        "moderate": "moderate", "modéré": "moderate", "modere": "moderate", "medium": "moderate",
        "high": "high", "élevé": "high", "elevé": "high", "active": "high", "very active": "high",
    }
    diet_bdd["physical_activity_level"] = diet_bdd["physical_activity_level"].str.strip().str.lower().map(act_map)

diet_bdd.to_csv(os.path.join(BDD_DIR, "diet_recommendations_bdd.csv"), index=False)
print(f"   ✅ {len(diet_bdd)} lignes — colonnes mappées vers schéma health_profiles, NULL conservés")

# ── 3. gym_members_exercise → users + user_metrics ────────────
print("🧹 [BDD] gym_members_exercise → users + user_metrics...")
gym_bdd = gym.copy()
gym_bdd = normalize_columns(gym_bdd)

# Renommages pour faciliter le load
gym_rename = {
    "workout_frequency_days_week": "workout_frequency_days_week",
}
gym_bdd = gym_bdd.rename(columns={k: v for k, v in gym_rename.items() if k in gym_bdd.columns})
gym_bdd.to_csv(os.path.join(BDD_DIR, "gym_members_exercise_bdd.csv"), index=False)
print(f"   ✅ {len(gym_bdd)} lignes — colonnes normalisées")

# ── 4. gym_members_synthetic → users + user_metrics (supplément)
print("🧹 [BDD] gym_members_synthetic → users + user_metrics (supplément)...")
synt_bdd = synt.copy()
synt_bdd["Max_BPM"] = pd.to_numeric(synt_bdd["Max_BPM"], errors='coerce')
synt_bdd = normalize_columns(synt_bdd)
synt_bdd.to_csv(os.path.join(BDD_DIR, "gym_members_synthetic_bdd.csv"), index=False)
print(f"   ✅ {len(synt_bdd)} lignes — Max_BPM corrigé, NULL conservés")


# ══════════════════════════════════════════════════════════════════
# NETTOYAGE ML
# Objectif : données pour entraîner des modèles
# Stratégie : NULL supprimés, texte encodé, valeurs normalisées
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("🤖 NETTOYAGE POUR LE MACHINE LEARNING")
print("=" * 55)

print("\n🧹 [ML] daily_food_nutrition...")
food_ml = food.drop_duplicates().copy()
food_ml = normalize_columns(food_ml)
food_ml = food_ml.dropna()
for col in food_ml.select_dtypes(include='object').columns:
    food_ml[col] = LabelEncoder().fit_transform(food_ml[col].astype(str))
cols_num = food_ml.select_dtypes(include=['int64', 'float64']).columns
food_ml[cols_num] = StandardScaler().fit_transform(food_ml[cols_num])
food_ml.to_csv(os.path.join(ML_DIR, "daily_food_nutrition_ml.csv"), index=False)
print(f"   ✅ {len(food_ml)} lignes — encodage + normalisation")

print("🧹 [ML] diet_recommendations...")
diet_ml = diet.copy()
diet_ml = normalize_columns(diet_ml)
diet_ml["disease_type"]         = diet_ml.get("disease_type",         pd.Series()).fillna("Non renseigné")
diet_ml["dietary_restrictions"] = diet_ml.get("dietary_restrictions", pd.Series()).fillna("Non renseigné")
diet_ml["allergies"]            = diet_ml.get("allergies",            pd.Series()).fillna("Non renseigné")
diet_ml = diet_ml.dropna()
for col in diet_ml.select_dtypes(include='object').columns:
    diet_ml[col] = LabelEncoder().fit_transform(diet_ml[col].astype(str))
cols_num = diet_ml.select_dtypes(include=['int64', 'float64']).columns
diet_ml[cols_num] = StandardScaler().fit_transform(diet_ml[cols_num])
diet_ml.to_csv(os.path.join(ML_DIR, "diet_recommendations_ml.csv"), index=False)
print(f"   ✅ {len(diet_ml)} lignes — encodage + normalisation")

print("🧹 [ML] gym_members_exercise...")
gym_ml = gym.copy()
gym_ml = normalize_columns(gym_ml)
gym_ml = gym_ml.dropna()
for col in gym_ml.select_dtypes(include='object').columns:
    gym_ml[col] = LabelEncoder().fit_transform(gym_ml[col].astype(str))
cols_num = gym_ml.select_dtypes(include=['int64', 'float64']).columns
gym_ml[cols_num] = StandardScaler().fit_transform(gym_ml[cols_num])
gym_ml.to_csv(os.path.join(ML_DIR, "gym_members_exercise_ml.csv"), index=False)
print(f"   ✅ {len(gym_ml)} lignes — encodage + normalisation")

print("🧹 [ML] gym_members_synthetic...")
synt_ml = synt.copy()
synt_ml["Max_BPM"] = pd.to_numeric(synt_ml["Max_BPM"], errors='coerce')
synt_ml = normalize_columns(synt_ml)
synt_ml = synt_ml.dropna()
for col in synt_ml.select_dtypes(include='object').columns:
    synt_ml[col] = LabelEncoder().fit_transform(synt_ml[col].astype(str))
cols_num = synt_ml.select_dtypes(include=['int64', 'float64']).columns
synt_ml[cols_num] = StandardScaler().fit_transform(synt_ml[cols_num])
synt_ml.to_csv(os.path.join(ML_DIR, "gym_members_synthetic_ml.csv"), index=False)
print(f"   ✅ {len(synt_ml)} lignes — encodage + normalisation")


# ══════════════════════════════════════════════════════════════════
# RAPPORT
# ══════════════════════════════════════════════════════════════════
with open(rapport_path, "w", encoding="utf-8") as f:
    f.write("# Rapport de nettoyage des données\n\n")
    f.write(f"**Projet** : HealthAI Coach — Backend Métier  \n")
    f.write(f"**Généré le** : {datetime.now().strftime('%d/%m/%Y à %H:%M')}  \n\n")
    f.write("---\n\n")
    f.write("## Stratégie de nettoyage\n\n")
    f.write("| Destination | Stratégie |\n|-------------|----------|\n")
    f.write("| BDD | Suppression doublons, correction types, NULL conservés, colonnes mappées vers schéma SQL |\n")
    f.write("| Machine Learning | Suppression NULL, encodage texte, normalisation StandardScaler |\n\n")
    f.write("---\n\n")
    f.write("## Bilan BDD\n\n")
    f.write("| Dataset | Table cible | Lignes | Actions |\n|---------|-------------|--------|---------|\n")
    f.write(f"| daily_food_nutrition  | nutrition_items  | {len(food_bdd)} | Doublons supprimés, colonnes renommées |\n")
    f.write(f"| diet_recommendations  | health_profiles  | {len(diet_bdd)} | Colonnes mappées, severity/activity normalisés |\n")
    f.write(f"| gym_members_exercise  | users + user_metrics | {len(gym_bdd)} | Colonnes normalisées |\n")
    f.write(f"| gym_members_synthetic | users + user_metrics | {len(synt_bdd)} | Max_BPM corrigé |\n\n")
    f.write("---\n\n")
    f.write("## Bilan Machine Learning\n\n")
    f.write("| Dataset | Lignes après nettoyage | Actions |\n|---------|------------------------|--------|\n")
    f.write(f"| daily_food_nutrition  | {len(food_ml)} | NULL supprimés, encodage, normalisation |\n")
    f.write(f"| diet_recommendations  | {len(diet_ml)} | NULL remplis/supprimés, encodage, normalisation |\n")
    f.write(f"| gym_members_exercise  | {len(gym_ml)} | NULL supprimés, encodage, normalisation |\n")
    f.write(f"| gym_members_synthetic | {len(synt_ml)} | NULL supprimés, encodage, normalisation |\n")

print(f"\n📄 Rapport nettoyage généré : {rapport_path}")
print("\n" + "=" * 55)
print("✅ NETTOYAGE V2 TERMINÉ")
print("=" * 55)
