"""Réponses de secours quand tous les services IA sont indisponibles."""


def nutrition_analyze_fallback(description: str) -> dict:
    return {
        "aliments": [{"nom": "Repas non identifié", "quantite": "1 portion", "calories": 500}],
        "nutrition": {"calories": 500, "proteines": 25.0, "glucides": 60.0, "lipides": 15.0},
        "score_sante": 5,
        "desequilibres": ["Analyse IA indisponible — données estimées"],
        "conseils": ["Consultez un nutritionniste pour une analyse précise."],
        "source": "fallback",
    }


def meal_plan_fallback(objectif: str, duree_jours: int) -> dict:
    repas_type = {
        "petit_dejeuner": {"nom": "Petit-déjeuner équilibré", "calories": 400, "ingredients": ["flocons d'avoine", "fruits", "lait"]},
        "dejeuner": {"nom": "Déjeuner complet", "calories": 700, "ingredients": ["protéine", "légumes", "féculents"]},
        "diner": {"nom": "Dîner léger", "calories": 500, "ingredients": ["salade", "protéine maigre", "légumes"]},
    }
    plan = [
        {
            "jour": j + 1,
            "petit_dejeuner": repas_type["petit_dejeuner"],
            "dejeuner": repas_type["dejeuner"],
            "diner": repas_type["diner"],
            "total_calories": 1600,
        }
        for j in range(duree_jours)
    ]
    return {"plan": plan, "source": "fallback"}


def activity_recommend_fallback(niveau: str) -> dict:
    exercices = [
        {"nom": "Marche rapide", "series": 1, "repetitions": "30 min", "repos_sec": 0},
        {"nom": "Pompes", "series": 3, "repetitions": "10", "repos_sec": 60},
        {"nom": "Squats", "series": 3, "repetitions": "15", "repos_sec": 60},
    ]
    return {
        "programme": [
            {"jour": j + 1, "type_seance": "Cardio + renforcement", "exercices": exercices, "duree_estimee_min": 45}
            for j in range(3)
        ],
        "conseils": ["Programme générique — service IA indisponible."],
        "source": "fallback",
    }
