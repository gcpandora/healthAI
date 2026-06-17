"""Orchestrateur principal — cascade Cache → HuggingFace → Ollama → Fallback."""

import logging
from app.services import cache_service, ollama_service, huggingface_service, fallback_service
from app.services import backend_client

logger = logging.getLogger(__name__)

SYSTEM_ANALYZE = """Tu es un expert en nutrition.
Retourne UNIQUEMENT un JSON valide sans markdown ni texte avant/après.
Structure obligatoire :
{
  "aliments": [{"nom": "string", "quantite": "string", "calories": int}],
  "nutrition": {"calories": int, "proteines": float, "glucides": float, "lipides": float},
  "score_sante": int,
  "desequilibres": ["string"],
  "conseils": ["string"]
}"""

SYSTEM_MEAL_PLAN = """Tu es un diététicien expert.
Retourne UNIQUEMENT un JSON valide sans markdown ni texte avant/après.
Structure obligatoire :
{
  "plan": [
    {
      "jour": int,
      "petit_dejeuner": {"nom": "string", "calories": int, "ingredients": ["string"]},
      "dejeuner": {"nom": "string", "calories": int, "ingredients": ["string"]},
      "diner": {"nom": "string", "calories": int, "ingredients": ["string"]},
      "total_calories": int
    }
  ]
}"""

SYSTEM_ACTIVITY = """Tu es un coach sportif expert.
Retourne UNIQUEMENT un JSON valide sans markdown ni texte avant/après.
Structure obligatoire :
{
  "programme": [
    {
      "jour": int,
      "type_seance": "string",
      "exercices": [{"nom": "string", "series": int, "repetitions": "string", "repos_sec": int}],
      "duree_estimee_min": int
    }
  ],
  "conseils": ["string"]
}"""


async def analyze_nutrition(description: str, health_goal: str, image_bytes: bytes | None = None) -> dict:
    cache_key = cache_service.make_key("analyze", {"desc": description, "goal": health_goal})
    cached = cache_service.get(cache_key)
    if cached:
        logger.info("[cascade] Cache hit — résultat servi depuis le cache")
        return cached

    aliments_desc = description

    # Étape 1 — HuggingFace (classification image)
    if image_bytes:
        logger.info("[cascade] Étape 1/3 — HuggingFace : classification de l'image...")
        try:
            labels = await huggingface_service.classify_image(image_bytes)
            aliments_desc = ", ".join(labels)
            logger.info("[cascade] HuggingFace OK — labels détectés : %s", aliments_desc)
        except Exception as exc:
            logger.warning("[cascade] HuggingFace KO (%s: %s) — passage à Ollama", type(exc).__name__, exc)
    else:
        logger.info("[cascade] Pas d'image — étape HuggingFace ignorée, description : %r", description)

    # Étape 2 — Ollama (analyse nutritionnelle LLM)
    logger.info("[cascade] Étape 2/3 — Ollama (%s) : génération de l'analyse...", "ollama" )
    try:
        result = await ollama_service.generate(
            SYSTEM_ANALYZE,
            f"Analyse ce repas (objectif: {health_goal}): {aliments_desc}",
        )
        result["source"] = "ollama"
        logger.info("[cascade] Ollama OK — source=ollama score_sante=%s", result.get("score_sante"))
        cache_service.set(cache_key, result)
        return result
    except Exception as exc:
        logger.warning("[cascade] Ollama KO (%s: %s) — activation du fallback", type(exc).__name__, exc)

    # Étape 3 — Fallback statique
    logger.warning("[cascade] Étape 3/3 — Fallback : valeurs estimées génériques retournées")
    result = fallback_service.nutrition_analyze_fallback(aliments_desc)
    cache_service.set(cache_key, result)
    return result


async def generate_meal_plan(objectif: str, calories_cible: int, duree_jours: int,
                              budget: str | None, regime: str | None, allergies: list[str]) -> dict:
    cache_key = cache_service.make_key("meal_plan", {
        "objectif": objectif, "cal": calories_cible, "jours": duree_jours,
        "budget": budget, "regime": regime, "allergies": allergies,
    })
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    user_msg = (
        f"Génère un plan de repas de {duree_jours} jours. "
        f"Objectif: {objectif}. Calories/jour: {calories_cible}. "
        f"Budget: {budget or 'moyen'}. Régime: {regime or 'aucun'}. "
        f"Allergies: {', '.join(allergies) if allergies else 'aucune'}."
    )
    try:
        result = await ollama_service.generate(SYSTEM_MEAL_PLAN, user_msg)
        result["source"] = "ollama"
        cache_service.set(cache_key, result)
        return result
    except Exception:
        result = fallback_service.meal_plan_fallback(objectif, duree_jours)
        cache_service.set(cache_key, result)
        return result


async def recommend_activity(
    objectif: str,
    niveau: str,
    duree_seance_min: int,
    equipements: list[str],
    limitations: list[str],
) -> dict:
    import logging
    logger = logging.getLogger(__name__)

    cache_key = cache_service.make_key("activity", {
        "objectif": objectif,
        "niveau": niveau,
        "duree": duree_seance_min,
        "equip": sorted(equipements),
        "limit": sorted(limitations),
    })
    cached = cache_service.get(cache_key)
    if cached:
        logger.info("Cache hit — activity recommend")
        return cached

    # 1. Micro-service MongoDB (source de vérité, critère P1 éliminatoire)
    niveau_map = {"debutant": 1, "intermediaire": 2, "avance": 3}
    mongo_payload = {
        "objective": objectif,
        "experience_level": niveau_map.get(niveau, 1),
        "limitations": limitations,
        "equipment": equipements,
    }
    logger.info("Appel micro-service MongoDB — objectif=%s niveau=%s", objectif, niveau)
    mongo_result = await backend_client.get_activity_recommendations(mongo_payload)

    if mongo_result:
        logger.info("MongoDB OK — workout_type=%s confidence=%s",
                    mongo_result.get("recommended_workout_type"),
                    mongo_result.get("confidence"))

        exercises = mongo_result.get("exercises", [])
        exercises_desc = ", ".join(ex["name"] for ex in exercises[:5]) or "exercices variés"

        # 2. Enrichissement Ollama (conseils en langage naturel, optionnel)
        user_msg = (
            f"Programme {mongo_result.get('recommended_workout_type', 'fitness')} "
            f"pour objectif '{objectif}', niveau '{niveau}', {duree_seance_min} min/séance. "
            f"Exercices : {exercises_desc}. "
            f"Donne uniquement 3 conseils d'entraînement et récupération, en français."
        )
        try:
            llm_result = await ollama_service.generate(SYSTEM_ACTIVITY, user_msg)
            conseils = llm_result.get("conseils", [])
            source = "mongodb+ollama"
        except Exception:
            conseils = [
                "Respectez les temps de repos entre chaque série.",
                "Hydratez-vous régulièrement pendant l'effort.",
                "Échauffez-vous 10 minutes avant de commencer.",
            ]
            source = "mongodb+fallback_conseils"

        result = {
            "programme": [
                {
                    "jour": i + 1,
                    "type_seance": mongo_result.get("recommended_workout_type", "fitness"),
                    "exercices": [
                        {
                            "nom": ex["name"],
                            "series": ex.get("sets", 3),
                            "repetitions": str(ex.get("reps", "12")),
                            "repos_sec": ex.get("rest_seconds", 60),
                        }
                        for ex in exercises
                    ],
                    "duree_estimee_min": duree_seance_min,
                }
                for i in range(3)
            ],
            "conseils": conseils,
            "source": source,
            "confidence": mongo_result.get("confidence", 0.5),
        }

    else:
        # 3. Fallback si MongoDB ET Ollama sont indisponibles
        logger.warning("Fallback activé — MongoDB et Ollama indisponibles")
        result = fallback_service.activity_recommend_fallback(niveau)
        result["source"] = "fallback_complet"

    cache_service.set(cache_key, result)
    return result
