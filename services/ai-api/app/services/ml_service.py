"""Chargement des modèles ML2 (pkl) et prédictions nutrition / niveau fitness."""

import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

ML_MODELS_PATH = os.getenv("ML_MODELS_PATH", "/app/models")

_nutrition_model = None
_nutrition_encoders = None
_nutrition_scaler = None
_nutrition_features = None

_fitness_model = None
_fitness_encoders = None
_fitness_scaler = None
_fitness_features = None


def _load():
    global _nutrition_model, _nutrition_encoders, _nutrition_scaler, _nutrition_features
    global _fitness_model, _fitness_encoders, _fitness_scaler, _fitness_features

    path = Path(ML_MODELS_PATH)

    try:
        _nutrition_model    = joblib.load(path / "model_nutrition.pkl")
        _nutrition_encoders = joblib.load(path / "encoders_diet.pkl")
        _nutrition_scaler   = joblib.load(path / "scaler_diet.pkl")
        _nutrition_features = joblib.load(path / "features_diet.pkl")
        print(f"[ML] Modèle nutrition chargé — {path}")
    except Exception as exc:
        print(f"[ML] Modèle nutrition indisponible : {exc}")

    try:
        _fitness_model    = joblib.load(path / "model_fitness_final.pkl")
        _fitness_encoders = joblib.load(path / "encoders_gym_final.pkl")
        _fitness_scaler   = joblib.load(path / "scaler_gym_final.pkl")
        _fitness_features = joblib.load(path / "features_gym_final.pkl")
        print(f"[ML] Modèle fitness chargé — {path}")
    except Exception as exc:
        print(f"[ML] Modèle fitness indisponible : {exc}")


_load()


def predict_diet(
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    physical_activity_level: str,
    weekly_exercise_hours: float,
    daily_caloric_intake: float,
) -> dict:
    if _nutrition_model is None:
        return {"diet_recommendation": "Balanced", "confidence": 0.0, "probabilities": {}, "source": "fallback"}

    bmi             = weight_kg / ((height_cm / 100) ** 2)
    caloric_density = daily_caloric_intake / weight_kg
    bmi_category    = (
        "underweight" if bmi < 18.5
        else "normal"     if bmi < 25
        else "overweight" if bmi < 30
        else "obese"
    )
    age_group = (
        "young"  if age <= 25
        else "adult"  if age <= 35
        else "middle" if age <= 50
        else "senior"
    )

    df = pd.DataFrame([{
        "age":                    age,
        "gender":                 gender,
        "weight_kg":              weight_kg,
        "height_cm":              height_cm,
        "bmi":                    bmi,
        "physical_activity_level": physical_activity_level,
        "weekly_exercise_hours":  weekly_exercise_hours,
        "daily_caloric_intake":   daily_caloric_intake,
        "caloric_density":        caloric_density,
        "bmi_category":           bmi_category,
        "age_group":              age_group,
    }])

    for col in ["gender", "physical_activity_level", "bmi_category", "age_group"]:
        le  = _nutrition_encoders[col]
        val = str(df[col].iloc[0])
        df[col] = le.transform([val])[0] if val in le.classes_ else 0

    cols_num = ["age", "weight_kg", "height_cm", "bmi",
                "weekly_exercise_hours", "daily_caloric_intake", "caloric_density"]
    df[cols_num] = _nutrition_scaler.transform(df[cols_num])

    X      = df[_nutrition_features].values
    pred   = _nutrition_model.predict(X)[0]
    proba  = _nutrition_model.predict_proba(X)[0]
    le_tgt = _nutrition_encoders["diet_recommendation"]
    label  = le_tgt.inverse_transform([pred])[0]

    return {
        "diet_recommendation": label,
        "confidence":          round(float(np.max(proba)), 3),
        "probabilities":       {cls: round(float(p), 3) for cls, p in zip(le_tgt.classes_, proba)},
        "source":              "ml2_random_forest",
    }


def predict_fitness_level(
    age: int,
    gender: str,
    weight_kg: float,
    height_m: float,
    max_bpm: int,
    avg_bpm: int,
    resting_bpm: int,
    session_duration_hours: float,
    calories_burned: float,
    fat_percentage: float,
    water_intake_liters: float,
    workout_frequency: float,
) -> dict:
    if _fitness_model is None:
        return {"experience_level": 1, "label": "Débutant", "confidence": 0.0, "probabilities": {}, "source": "fallback"}

    bmi = weight_kg / (height_m ** 2)

    df = pd.DataFrame([{
        "age":                          age,
        "gender":                       gender,
        "weight_kg":                    weight_kg,
        "height_m":                     height_m,
        "bmi":                          bmi,
        "max_bpm":                      max_bpm,
        "avg_bpm":                      avg_bpm,
        "resting_bpm":                  resting_bpm,
        "session_duration_hours":       session_duration_hours,
        "calories_burned":              calories_burned,
        "fat_percentage":               fat_percentage,
        "water_intake_liters":          water_intake_liters,
        "workout_frequency_days/week":  workout_frequency,
    }])

    le_g = _fitness_encoders["gender"]
    val  = str(df["gender"].iloc[0])
    df["gender"] = le_g.transform([val])[0] if val in le_g.classes_ else 0

    cols_num = [
        "age", "weight_kg", "height_m", "bmi",
        "max_bpm", "avg_bpm", "resting_bpm",
        "session_duration_hours", "calories_burned",
        "fat_percentage", "water_intake_liters",
        "workout_frequency_days/week",
    ]
    df[cols_num] = _fitness_scaler.transform(df[cols_num])

    X     = df[_fitness_features].values
    pred  = _fitness_model.predict(X)[0]
    proba = _fitness_model.predict_proba(X)[0]

    labels = {1: "Débutant", 2: "Intermédiaire", 3: "Avancé"}

    return {
        "experience_level": int(pred),
        "label":            labels.get(int(pred), "Inconnu"),
        "confidence":       round(float(np.max(proba)), 3),
        "probabilities":    {labels.get(int(c), str(c)): round(float(p), 3)
                             for c, p in zip(_fitness_model.classes_, proba)},
        "source":           "ml2_random_forest",
    }
