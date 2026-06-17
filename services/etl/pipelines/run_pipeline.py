
import sys
import os
from loguru import logger
from datetime import datetime

# ── Résolution du répertoire courant pour les imports ──────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Chemins depuis variables d'environnement Docker ────────────
RAPPORT_DIR = os.getenv("RAPPORT_DIR", "/app/rapport")
os.makedirs(RAPPORT_DIR, exist_ok=True)

# ── Configuration logs ──────────────────────────────────────────
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)
logger.add(
    os.path.join(RAPPORT_DIR, "pipeline.log"),
    level="INFO",
    rotation="1 MB",
    encoding="utf-8"
)


def run_pipeline():
    debut = datetime.now()
    logger.info("=" * 55)
    logger.info("=== Démarrage du pipeline ETL HealthAI Coach ===")
    logger.info(f"Heure de démarrage : {debut.strftime('%d/%m/%Y à %H:%M:%S')}")
    logger.info("=" * 55)

    # ── Étape 1 : Extract ──────────────────────────────────────
    logger.info("Étape 1/3 : Extraction et inventaire des données")
    try:
        import ingestion  # noqa: F401
        logger.success("✅ Extraction terminée — rapport_inventaire.md généré")
    except Exception as e:
        logger.error(f"❌ Extraction échouée : {e}")
        sys.exit(1)

    # ── Étape 2 : Transform ────────────────────────────────────
    logger.info("Étape 2/3 : Nettoyage et transformation")
    try:
        import nettoyage_v2  # noqa: F401
        logger.success("✅ Nettoyage terminé — BDD + ML séparés, rapport_nettoyage_v2.md généré")
    except Exception as e:
        logger.error(f"❌ Nettoyage échoué : {e}")
        sys.exit(1)

    # ── Étape 3 : Load ─────────────────────────────────────────
    logger.info("Étape 3/3 : Chargement en base PostgreSQL")
    try:
        import load

        logger.info("  → Chargement nutrition_items...")
        n_nutrition = load.load_nutrition_items()

        logger.info("  → Chargement users + user_metrics...")
        n_users = load.load_users_and_metrics()

        logger.info("  → Chargement health_profiles...")
        n_profiles = load.load_health_profiles()

        logger.info("  → Chargement exercises (simulé)...")
        n_exercises = load.load_exercises()

        logger.success(
            f"✅ Load terminé — "
            f"{n_nutrition} aliments | "
            f"{n_users} utilisateurs | "
            f"{n_profiles} profils santé | "
            f"{n_exercises} exercices"
        )
    except Exception as e:
        logger.error(f"❌ Load échoué : {e}")
        sys.exit(1)

    # ── Bilan ──────────────────────────────────────────────────
    fin   = datetime.now()
    duree = (fin - debut).seconds
    logger.info("=" * 55)
    logger.success(f"✅ Pipeline ETL terminé en {duree} secondes")
    logger.info(f"Rapports disponibles dans : {RAPPORT_DIR}")
    logger.info("=" * 55)


if __name__ == "__main__":
    run_pipeline()
