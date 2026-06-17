import pandas as pd
import os
from datetime import datetime

# ── Chemins depuis variables d'environnement Docker ────────────
# DATA_DIR et RAPPORT_DIR sont définis dans docker-compose.yml
# Valeurs par défaut pour exécution locale hors Docker
DATA_DIR    = os.getenv("DATA_DIR",    "/app/data/raw")
RAPPORT_DIR = os.getenv("RAPPORT_DIR", "/app/rapport")

os.makedirs(RAPPORT_DIR, exist_ok=True)

rapport_path = os.path.join(RAPPORT_DIR, "rapport_inventaire.md")

DATASETS = {
    "daily_food_nutrition":  "daily_food_nutrition_dataset.csv",
    "diet_recommendations":  "diet_recommendations_dataset.csv",
    "gym_members_exercise":  "gym_members_exercise_tracking.csv",
    "gym_members_synthetic": "gym_members_exercise_tracking_synthetic_data.csv",
}

rapports = []

for name, file in DATASETS.items():
    path = os.path.join(DATA_DIR, file)
    try:
        df             = pd.read_csv(path, on_bad_lines='skip')
        nb_lignes      = len(df)
        nb_colonnes    = len(df.columns)
        nb_doublons    = df.duplicated().sum()
        valeurs_manq   = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
        types_colonnes = df.dtypes.astype(str).to_dict()

        rapports.append({
            "name":     name,
            "file":     file,
            "status":   "OK",
            "lignes":   nb_lignes,
            "colonnes": nb_colonnes,
            "doublons": nb_doublons,
            "manquants": valeurs_manq,
            "types":    types_colonnes,
        })

        print(f"✅ {name} — {nb_lignes} lignes x {nb_colonnes} colonnes")
        print(f"   Doublons : {nb_doublons}")
        print(f"   Valeurs manquantes : {valeurs_manq if valeurs_manq else 'aucune'}\n")

    except Exception as e:
        rapports.append({
            "name": name, "file": file, "status": f"ERREUR : {e}",
            "lignes": 0, "colonnes": 0, "doublons": 0, "manquants": {}, "types": {}
        })
        print(f"❌ {name} : {e}\n")

with open(rapport_path, "w", encoding="utf-8") as f:
    f.write("# Rapport d'inventaire des sources de données\n\n")
    f.write(f"**Projet** : HealthAI Coach — Backend Métier  \n")
    f.write(f"**Généré le** : {datetime.now().strftime('%d/%m/%Y à %H:%M')}  \n\n")
    f.write("---\n\n")

    for r in rapports:
        f.write(f"## {r['name']}\n\n")
        f.write("| Propriété | Valeur |\n")
        f.write("|-----------|--------|\n")
        f.write(f"| Fichier   | `{r['file']}` |\n")
        f.write(f"| Statut    | {r['status']} |\n")
        f.write(f"| Lignes    | {r['lignes']} |\n")
        f.write(f"| Colonnes  | {r['colonnes']} |\n")
        f.write(f"| Doublons  | {r['doublons']} |\n")

        if r['manquants']:
            f.write("\n**Valeurs manquantes :**\n\n")
            for col, nb in r['manquants'].items():
                f.write(f"- `{col}` : {nb} valeurs manquantes\n")
        else:
            f.write("\n✅ Aucune valeur manquante\n")

        if r['types']:
            f.write("\n**Types des colonnes :**\n\n")
            for col, typ in r['types'].items():
                f.write(f"- `{col}` : {typ}\n")

        f.write("\n---\n\n")

print(f"📄 Rapport généré : {rapport_path}")
