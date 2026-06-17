import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import os

# ── Configuration ─────────────────────────────────────────
DATA_DIR   = r"C:\Users\houss\Desktop\healthai-coach\data\clean"
OUTPUT_DIR = r"C:\Users\houss\Desktop\healthai-coach\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Chargement ─────────────────────────────────────────────
print("📥 Chargement des données...")
df = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_clean.csv"))
print(f"✅ {len(df)} lignes chargées\n")

# ── Sélection des colonnes pour le clustering ──────────────
colonnes = [
    "age",
    "weight_kg",
    "bmi",
    "calories_burned",
    "workout_frequency_days/week",
    "experience_level",
    "session_duration_hours"
]

df_ml = df[colonnes].dropna()
print(f"✅ Colonnes sélectionnées : {colonnes}")
print(f"✅ Lignes après nettoyage : {len(df_ml)}\n")

# ── Normalisation ──────────────────────────────────────────
print("⚙️ Normalisation des données...")
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_ml)
print("✅ Normalisation terminée\n")

# ── Trouver le bon nombre de clusters (méthode coude) ──────
print("📊 Calcul du nombre optimal de clusters...")
inerties = []
silhouettes = []
K = range(2, 8)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df_scaled)
    inerties.append(kmeans.inertia_)
    silhouettes.append(silhouette_score(df_scaled, kmeans.labels_))
    print(f"   k={k} → inertie={kmeans.inertia_:.0f} | silhouette={silhouette_score(df_scaled, kmeans.labels_):.3f}")

# Graphique méthode du coude
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(K, inerties, 'bo-')
plt.xlabel("Nombre de clusters")
plt.ylabel("Inertie")
plt.title("Méthode du coude")

plt.subplot(1, 2, 2)
plt.plot(K, silhouettes, 'go-')
plt.xlabel("Nombre de clusters")
plt.ylabel("Score silhouette")
plt.title("Score silhouette")

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "clustering_coude.png"))
plt.close()
print("\n✅ Graphique sauvegardé : clustering_coude.png\n")

# ── Modèle final avec k=3 ──────────────────────────────────
print("🤖 Entraînement du modèle K-Means (k=3)...")
kmeans_final = KMeans(n_clusters=3, random_state=42, n_init=10)
df_ml["cluster"] = kmeans_final.fit_predict(df_scaled)

# Labels lisibles
labels = {0: "Débutant", 1: "Intermédiaire", 2: "Expert"}
df_ml["profil"] = df_ml["cluster"].map(labels)

print("✅ Clusters créés\n")
print(df_ml["profil"].value_counts())

# ── Visualisation des clusters ─────────────────────────────
plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=df_ml,
    x="calories_burned",
    y="bmi",
    hue="profil",
    palette=["#2ecc71", "#3498db", "#e74c3c"],
    s=80,
    alpha=0.7
)
plt.title("Clustering des membres — Calories vs BMI")
plt.xlabel("Calories brûlées")
plt.ylabel("BMI")
plt.legend(title="Profil")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "clustering_resultats.png"))
plt.close()
print("\n✅ Graphique sauvegardé : clustering_resultats.png")

# ── Statistiques par cluster ───────────────────────────────
print("\n📊 Statistiques par profil :")
stats = df_ml.groupby("profil")[colonnes].mean().round(2)
print(stats)

# Sauvegarde résultats
df_ml.to_csv(os.path.join(OUTPUT_DIR, "clustering_resultats.csv"), index=False)
print("\n💾 Résultats sauvegardés : clustering_resultats.csv")
print("\n" + "="*50)
print("✅ CLUSTERING TERMINÉ")
print("="*50)