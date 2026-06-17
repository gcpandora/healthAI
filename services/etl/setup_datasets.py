"""
HealthAI Coach — Setup Datasets
Script d'installation et vérification des datasets Kaggle.

Usage:
    python setup_datasets.py
"""
import os
import sys
import zipfile
from pathlib import Path

# ── Couleurs pour terminal ──────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ── Chemins ────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_BDD_DIR = DATA_DIR / "clean_bdd"
CLEAN_ML_DIR = DATA_DIR / "clean_ml"

# ── Datasets Kaggle attendus ───────────────────────────────────
REQUIRED_FILES = {
    "daily_food_nutrition_dataset.csv": "Daily Food & Nutrition Dataset",
    "diet_recommendations_dataset.csv": "Diet Recommendations",
    "gym_members_exercise_tracking.csv": "Gym Members Exercise Tracking",
    "gym_members_exercise_tracking_synthetic_data.csv": "Gym Members Synthetic Data",
}


def print_header(text):
    """Afficher un titre formaté."""
    print(f"\n{BOLD}{text}{RESET}")
    print("=" * 60)


def print_success(text):
    """Afficher un message de succès."""
    print(f"{GREEN}✅ {text}{RESET}")


def print_warning(text):
    """Afficher un message d'avertissement."""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_error(text):
    """Afficher un message d'erreur."""
    print(f"{RED}❌ {text}{RESET}")


def create_directories():
    """Créer la structure de répertoires."""
    print_header("Création de la structure de répertoires")
    
    for directory in [RAW_DIR, CLEAN_BDD_DIR, CLEAN_ML_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        print_success(f"Répertoire créé/vérifié : {directory.relative_to(SCRIPT_DIR)}")


def extract_zip_files():
    """Extraire les fichiers ZIP si nécessaire."""
    print_header("Extraction des fichiers ZIP")
    
    zip_files = RAW_DIR.glob("*.zip")
    found_any = False
    
    for zip_file in zip_files:
        found_any = True
        try:
            print(f"Extraction de : {zip_file.name}")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(RAW_DIR)
            print_success(f"Exrait : {zip_file.name}")
            
            # Optionnel : supprimer le ZIP après extraction
            # zip_file.unlink()
        except Exception as e:
            print_error(f"Erreur lors de l'extraction de {zip_file.name}: {e}")
    
    if not found_any:
        print_warning("Aucun fichier ZIP trouvé dans data/raw/")


def verify_datasets():
    """Vérifier la présence et l'intégrité des datasets."""
    print_header("Vérification des datasets")
    
    missing = []
    found = []
    
    for filename, description in REQUIRED_FILES.items():
        filepath = RAW_DIR / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print_success(f"{description}")
            print(f"   → {filename} ({size_mb:.2f} MB)")
            found.append(filename)
        else:
            print_error(f"{description}")
            print(f"   → {filename} (MANQUANT)")
            missing.append(filename)
    
    return len(missing) == 0, missing


def check_csv_files():
    """Vérifier si les CSV peuvent être ouverts."""
    print_header("Vérification de l'intégrité des CSV")
    
    try:
        import pandas as pd
        all_ok = True
        
        for filename in REQUIRED_FILES.keys():
            filepath = RAW_DIR / filename
            if filepath.exists():
                try:
                    df = pd.read_csv(filepath, nrows=1)
                    rows = len(pd.read_csv(filepath))
                    print_success(f"{filename} : {rows} lignes, {len(df.columns)} colonnes")
                except Exception as e:
                    print_error(f"{filename} : {e}")
                    all_ok = False
        
        return all_ok
    except ImportError:
        print_warning("pandas non installé. Skipping CSV validation.")
        return None


def print_next_steps():
    """Afficher les prochaines étapes."""
    print_header("Prochaines étapes")
    print("""
1. ✅ Vérifiez que tous les datasets sont présents dans services/etl/data/raw/

2. 🏃 Lancez le pipeline ETL :
   
   Option A - Depuis Docker:
   $ docker compose up etl
   
   Option B - Localement:
   $ cd services/etl
   $ pip install -r requirements.txt
   $ python pipelines/run_pipeline.py

3. 📊 Vérifiez les rapports générés :
   
   $ cat rapport/rapport_inventaire.md
   $ cat rapport/rapport_nettoyage_v2.md

4. 🔍 Interrogez PostgreSQL to check les données chargées :
   
   $ psql postgresql://healthai_user:password@postgres:5432/healthai_db
   > SELECT COUNT(*) FROM nutrition_items;
    """)


def main():
    """Fonction principale."""
    print(f"\n{BOLD}{GREEN}🏥 HealthAI Coach — Setup Datasets{RESET}\n")
    
    # 1. Créer les répertoires
    create_directories()
    
    # 2. Extraire les ZIP si présents
    extract_zip_files()
    
    # 3. Vérifier les datasets
    all_present, missing = verify_datasets()
    
    if not all_present:
        print_error(f"\n{len(missing)} dataset(s) manquant(s) :")
        for m in missing:
            print(f"   - {m}")
        
        print_warning("""
Téléchargez les datasets manuellement :

  1. Créez un compte Kaggle : https://www.kaggle.com
  2. Téléchargez l'API Kaggle depuis Paramètres > API
  3. Placez kaggle.json dans ~/.kaggle/ (Unix) ou C:\\Users\\<USER>\\.kaggle\\ (Windows)
  4. Installez kaggle : pip install kaggle
  5. Téléchargez les datasets :
  
     kaggle datasets download -d sootersaalu/daily-nutrition
     kaggle datasets download -d timmofeyp/diet
     kaggle datasets download -d niharika41298/gym-members-exercise-dataset
     
  6. Décompressez les ZIP dans services/etl/data/raw/
  7. Relancez ce script.
        """)
        sys.exit(1)
    
    # 4. Vérifier l'intégrité des CSV
    csv_ok = check_csv_files()
    
    if csv_ok is False:
        print_error("Certains fichiers CSV sont corrompus.")
        sys.exit(1)
    
    # 5. Afficher les prochaines étapes
    print_next_steps()
    print_success(f"\n🎉 Setup complété ! Les datasets sont prêts.\n")


if __name__ == "__main__":
    main()
