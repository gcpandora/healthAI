import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

TRAINING_DATA_PATH = os.getenv(
    "TRAINING_DATA_PATH",
    "/app/training_data/gym_members_exercise_tracking.csv"
)

# Mapping objectif → types d'entraînement prioritaires (règles expertes)
OBJECTIVE_RULES = {
    "weight_loss":    ["HIIT", "Cardio"],
    "muscle_gain":    ["Strength"],
    "endurance":      ["Cardio", "HIIT"],
    "flexibility":    ["Yoga"],
    "general_fitness": None,  # laissé au modèle ML
}

# Limitations → exercices à exclure
LIMITATION_EXCLUSIONS = {
    "back_pain":  ["Soulevé de terre", "Box Jumps"],
    "knee_pain":  ["Course à pied", "Squat barre", "Box Jumps", "Jumping Jacks"],
    "shoulder_pain": ["Développé couché", "Développé militaire", "Tractions"],
}


class WorkoutRecommender:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.metrics = {}
        self._train()

    def _train(self):
        if not os.path.exists(TRAINING_DATA_PATH):
            print(f"[ML] Fichier d'entraînement introuvable : {TRAINING_DATA_PATH}")
            print("[ML] Modèle basé sur règles expertes uniquement.")
            return

        df = pd.read_csv(TRAINING_DATA_PATH)
        df.columns = df.columns.str.strip()

        df["Gender_enc"] = (df["Gender"] == "Male").astype(int)
        df["BMI"] = df["Weight (kg)"] / (df["Height (m)"] ** 2)

        features = [
            "Age", "Gender_enc", "Weight (kg)", "Height (m)", "BMI",
            "Experience_Level", "Workout_Frequency (days/week)",
            "Session_Duration (hours)", "Calories_Burned", "Max_BPM",
        ]
        df = df.dropna(subset=features + ["Workout_Type"])

        X = df[features].values
        y = self.label_encoder.fit_transform(df["Workout_Type"])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        self.metrics = {
            "accuracy": round(report["accuracy"], 3),
            "f1_macro": round(report["macro avg"]["f1-score"], 3),
            "classes": self.label_encoder.classes_.tolist(),
        }
        print(f"[ML] Modèle entraîné — accuracy={self.metrics['accuracy']} f1={self.metrics['f1_macro']}")

    def predict(self, age: int, gender: str, weight_kg: float, height_m: float,
                experience_level: int, workout_frequency: int = 3) -> dict:
        bmi = weight_kg / (height_m ** 2)
        gender_enc = 1 if gender == "Male" else 0

        if self.model is None:
            return {"workout_type": "Cardio", "probabilities": {}, "confidence": 0.0}

        X = np.array([[age, gender_enc, weight_kg, height_m, bmi, experience_level, workout_frequency]])
        proba = self.model.predict_proba(X)[0]
        classes = self.label_encoder.classes_

        scores = {cls: round(float(p), 3) for cls, p in zip(classes, proba)}
        best_idx = int(np.argmax(proba))

        return {
            "workout_type": classes[best_idx],
            "probabilities": scores,
            "confidence": round(float(proba[best_idx]), 3),
        }

    def recommend_workout_type(self, objective: str, age: int, gender: str,
                                weight_kg: float, height_m: float,
                                experience_level: int) -> tuple[str, float, dict]:
        ml_result = self.predict(age, gender, weight_kg, height_m, experience_level)
        priority_types = OBJECTIVE_RULES.get(objective)

        if priority_types:
            # Règle experte : choisir le meilleur score parmi les types autorisés
            scores = ml_result["probabilities"]
            best_type = max(priority_types, key=lambda t: scores.get(t, 0))
            confidence = scores.get(best_type, 0.5)
        else:
            best_type = ml_result["workout_type"]
            confidence = ml_result["confidence"]

        return best_type, confidence, ml_result["probabilities"]

    def filter_exercises(self, exercises: list, limitations: list,
                          equipment: list, experience_level: int) -> list:
        excluded = set()
        for limitation in limitations:
            excluded.update(LIMITATION_EXCLUSIONS.get(limitation, []))

        result = []
        for ex in exercises:
            if ex["name"] in excluded:
                continue
            if ex["difficulty"] > experience_level + 1:
                continue
            if ex["equipment"] and equipment:
                if not any(e in equipment for e in ex["equipment"]) and ex["equipment"] != []:
                    if experience_level < 2:
                        continue
            result.append(ex)
        return result

    def build_weekly_program(self, workout_type: str, objective: str,
                              experience_level: int) -> dict:
        freq = {1: 3, 2: 4, 3: 5}.get(experience_level, 3)
        duration = {1: 30, 2: 45, 3: 60}.get(experience_level, 40)

        return {
            "sessions_per_week": freq,
            "session_duration_minutes": duration,
            "workout_type": workout_type,
            "objective": objective,
            "notes": (
                "Commencez à intensité modérée" if experience_level == 1
                else "Augmentez progressivement la charge" if experience_level == 2
                else "Maintenez une haute intensité avec bonne récupération"
            ),
        }


recommender = WorkoutRecommender()
