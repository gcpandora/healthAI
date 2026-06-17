"""
HealthAI Coach — MSPR 2
Pipeline Random Forest — Recommandation Nutritionnelle (FINAL)
Score honnête : ~46% F1-score
Compétences : DIADS2.1, DIADS2.3, DIADS2.4, DIADS2.5, DIADS2.6
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score, precision_score, recall_score
)

# ══════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════
BASE_DIR    = r"C:\Users\houss\Desktop\healthai\healthAI\services\ml2"
DATA_PATH   = os.path.join(BASE_DIR, "data", "clean_bdd", "diet_recommendations_bdd.csv")
ML_DIR      = os.path.join(BASE_DIR, "data", "clean_ml")
MODEL_DIR   = os.path.join(BASE_DIR, "models")
OUTPUT_DIR  = os.path.join(BASE_DIR, "outputs")
RAPPORT_DIR = os.path.join(BASE_DIR, "rapport")

for d in [ML_DIR, MODEL_DIR, OUTPUT_DIR, RAPPORT_DIR]:
    os.makedirs(d, exist_ok=True)

debut = datetime.now()

print("=" * 60)
print("PIPELINE RANDOM FOREST FINAL — NUTRITION")
print("HealthAI Coach MSPR 2")
print("=" * 60)

# ══════════════════════════════════════════════════════
# ÉTAPE 1 — CHARGEMENT ET NETTOYAGE
# ══════════════════════════════════════════════════════
print("\n📥 ÉTAPE 1 — CHARGEMENT ET NETTOYAGE")
print("-" * 60)

df = pd.read_csv(DATA_PATH)
nb_lignes_brutes = len(df)
manquants_avant  = df.isnull().sum()[df.isnull().sum() > 0].to_dict()

print(f"   Lignes brutes : {nb_lignes_brutes}")
print(f"   Colonnes      : {len(df.columns)}")

df = df.drop_duplicates()
df = df.drop(columns=['patient_id'])
df['disease_type']         = df['disease_type'].fillna('None')
df['dietary_restrictions'] = df['dietary_restrictions'].fillna('None')
df['allergies']            = df['allergies'].fillna('None')

print(f"   Lignes après  : {len(df)}")
print(f"   Manquants     : {df.isnull().sum().sum()}")

# ══════════════════════════════════════════════════════
# ÉTAPE 2 — FEATURE ENGINEERING
# ══════════════════════════════════════════════════════
print("\n🔧 ÉTAPE 2 — FEATURE ENGINEERING")
print("-" * 60)

df_ml = df.copy()

df_ml['bmi'] = df_ml['weight_kg'] / ((df_ml['height_cm'] / 100) ** 2)
print("   ✅ bmi recalculé depuis weight_kg et height_cm")

df_ml['caloric_density'] = df_ml['daily_caloric_intake'] / df_ml['weight_kg']
print("   ✅ caloric_density = calories / poids")

df_ml['bmi_category'] = pd.cut(
    df_ml['bmi'],
    bins=[0, 18.5, 25, 30, 100],
    labels=['underweight', 'normal', 'overweight', 'obese']
).astype(str)
print("   ✅ bmi_category depuis bmi")

df_ml['age_group'] = pd.cut(
    df_ml['age'],
    bins=[0, 25, 35, 50, 100],
    labels=['young', 'adult', 'middle', 'senior']
).astype(str)
print("   ✅ age_group depuis age")

# ══════════════════════════════════════════════════════
# ÉTAPE 3 — SÉLECTION DES FEATURES
# ══════════════════════════════════════════════════════
print("\n🔍 ÉTAPE 3 — SÉLECTION DES FEATURES")
print("-" * 60)

colonnes_retirees = {
    'patient_id':                      'Identifiant technique inutile pour le ML',
    'disease_type':                    'Data leakage — corrélation parfaite avec la cible',
    'severity':                        'Liée à disease_type — data leakage indirect',
    'dietary_restrictions':            'Data leakage — corrélée à la cible',
    'allergies':                       'Data leakage — corrélée à la cible',
    'preferred_cuisine':               'Data leakage — corrélée à la cible',
    'cholesterol_mg/dl':               'Nécessite prise de sang — inaccessible utilisateur lambda',
    'blood_pressure_mmhg':             'Nécessite tensiomètre — inaccessible utilisateur lambda',
    'glucose_mg/dl':                   'Nécessite analyse sanguine — inaccessible utilisateur lambda',
    'adherence_to_diet_plan':          'Donnée subjective — dégrade les performances',
    'dietary_nutrient_imbalance_score':'Calculé par professionnel — dégrade les performances',
}

print("\n   COLONNES RETIRÉES :")
for col, raison in colonnes_retirees.items():
    print(f"   ❌ {col} → {raison}")

features = [
    'age',
    'gender',
    'weight_kg',
    'height_cm',
    'bmi',
    'physical_activity_level',
    'weekly_exercise_hours',
    'daily_caloric_intake',
    'caloric_density',
    'bmi_category',
    'age_group',
]

print("\n   FEATURES UTILISÉES :")
for feat in features:
    print(f"   ✅ {feat}")
print(f"\n   Total : {len(features)} features")

# ══════════════════════════════════════════════════════
# ÉTAPE 4 — ENCODAGE ET NORMALISATION
# ══════════════════════════════════════════════════════
print("\n🔠 ÉTAPE 4 — ENCODAGE ET NORMALISATION")
print("-" * 60)

encoders = {}
cols_to_encode = ['gender', 'physical_activity_level', 'bmi_category', 'age_group']

for col in cols_to_encode:
    le = LabelEncoder()
    df_ml[col] = le.fit_transform(df_ml[col].astype(str))
    encoders[col] = le
    print(f"   {col} → {list(le.classes_)}")

le_target = LabelEncoder()
df_ml['diet_recommendation'] = le_target.fit_transform(df_ml['diet_recommendation'])
encoders['diet_recommendation'] = le_target
print(f"\n   Cible : {dict(enumerate(le_target.classes_))}")

cols_num = [
    'age', 'weight_kg', 'height_cm', 'bmi',
    'weekly_exercise_hours', 'daily_caloric_intake',
    'caloric_density'
]

scaler = StandardScaler()
df_ml[cols_num] = scaler.fit_transform(df_ml[cols_num])
print(f"\n   {len(cols_num)} colonnes normalisées")

df_ml.to_csv(os.path.join(ML_DIR, "diet_recommendations_ml.csv"), index=False)

# ══════════════════════════════════════════════════════
# ÉTAPE 5 — SPLIT TRAIN/TEST
# ══════════════════════════════════════════════════════
print("\n✂️  ÉTAPE 5 — SPLIT TRAIN/TEST")
print("-" * 60)

X = df_ml[features]
y = df_ml['diet_recommendation']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train : {len(X_train)} lignes (80%)")
print(f"   Test  : {len(X_test)} lignes (20%)")

# ══════════════════════════════════════════════════════
# ÉTAPE 6 — MODÈLE DE BASE
# ══════════════════════════════════════════════════════
print("\n🌲 ÉTAPE 6 — RANDOM FOREST DE BASE")
print("-" * 60)

rf_base = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',
    random_state=42
)
rf_base.fit(X_train, y_train)
y_pred_base = rf_base.predict(X_test)

acc_base = accuracy_score(y_test, y_pred_base)
f1_base  = f1_score(y_test, y_pred_base, average='weighted')

print(f"   Accuracy : {acc_base:.4f}")
print(f"   F1-score : {f1_base:.4f}")
print(classification_report(y_test, y_pred_base, target_names=le_target.classes_))

# ══════════════════════════════════════════════════════
# ÉTAPE 7 — OPTIMISATION GRIDSEARCHCV
# ══════════════════════════════════════════════════════
print("\n⚙️  ÉTAPE 7 — OPTIMISATION GRIDSEARCHCV")
print("-" * 60)

param_grid = {
    'n_estimators':      [100, 200, 300],
    'max_depth':         [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf':  [1, 2, 4],
    'class_weight':      ['balanced', None]
}

grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid, cv=5,
    scoring='f1_weighted',
    n_jobs=-1, verbose=1
)
grid.fit(X_train, y_train)

best_model  = grid.best_estimator_
y_pred_best = best_model.predict(X_test)

acc_best = accuracy_score(y_test, y_pred_best)
f1_best  = f1_score(y_test, y_pred_best, average='weighted')
pr_best  = precision_score(y_test, y_pred_best, average='weighted')
re_best  = recall_score(y_test, y_pred_best, average='weighted')
cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='f1_weighted')

print(f"\n   Meilleurs paramètres : {grid.best_params_}")
print(f"   Accuracy optimisé   : {acc_best:.4f}")
print(f"   F1-score optimisé   : {f1_best:.4f}")
print(f"   CV F1 moyen         : {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
print(f"\n   Rapport de classification :")
print(classification_report(y_test, y_pred_best, target_names=le_target.classes_))

# ══════════════════════════════════════════════════════
# ÉTAPE 8 — VISUALISATIONS
# ══════════════════════════════════════════════════════
print("\n📊 ÉTAPE 8 — VISUALISATIONS")
print("-" * 60)

# Matrice de confusion
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred_best)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=le_target.classes_,
            yticklabels=le_target.classes_)
plt.title('Matrice de confusion — Nutrition RF Final')
plt.ylabel('Réel')
plt.xlabel('Prédit')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix_nutrition_final.png"), dpi=150)
plt.close()
print("   ✅ Matrice de confusion")

# Importance des features
feat_imp = pd.Series(
    best_model.feature_importances_, index=features
).sort_values(ascending=False)
plt.figure(figsize=(12, 6))
feat_imp.plot(kind='bar', color='steelblue', edgecolor='white')
plt.title('Importance des features — Nutrition RF Final')
plt.ylabel('Importance')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "feature_importance_nutrition_final.png"), dpi=150)
plt.close()
print("   ✅ Importance des features")

# Comparaison base vs optimisé
fig, ax = plt.subplots(figsize=(8, 6))
x = range(2)
bars1 = ax.bar([i - 0.2 for i in x], [acc_base, acc_best], 0.4, label='Accuracy', color='steelblue')
bars2 = ax.bar([i + 0.2 for i in x], [f1_base,  f1_best],  0.4, label='F1-score',  color='coral')
ax.set_xticks(x)
ax.set_xticklabels(['RF Base', 'RF Optimisé'])
ax.set_ylim(0, 1)
ax.set_title('Comparaison RF Base vs Optimisé')
ax.set_ylabel('Score')
ax.legend()
for bar in list(bars1) + list(bars2):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f'{bar.get_height():.2f}',
        ha='center', va='bottom', fontsize=10
    )
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "comparaison_rf_nutrition_final.png"), dpi=150)
plt.close()
print("   ✅ Comparaison base vs optimisé")

# Distribution cible
plt.figure(figsize=(8, 5))
dist = pd.Series(le_target.inverse_transform(y)).value_counts()
dist.plot(kind='bar', color=['steelblue', 'coral', 'mediumseagreen'], edgecolor='white')
plt.title('Distribution des classes — Variable cible')
plt.ylabel('Effectif')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "distribution_cible_nutrition_final.png"), dpi=150)
plt.close()
print("   ✅ Distribution cible")

# ══════════════════════════════════════════════════════
# ÉTAPE 9 — SAUVEGARDE POUR L'API
# ══════════════════════════════════════════════════════
print("\n💾 ÉTAPE 9 — SAUVEGARDE POUR L'API")
print("-" * 60)

joblib.dump(best_model, os.path.join(MODEL_DIR, "model_nutrition.pkl"))
joblib.dump(encoders,   os.path.join(MODEL_DIR, "encoders_diet.pkl"))
joblib.dump(scaler,     os.path.join(MODEL_DIR, "scaler_diet.pkl"))
joblib.dump(features,   os.path.join(MODEL_DIR, "features_diet.pkl"))

print("   ✅ model_nutrition.pkl")
print("   ✅ encoders_diet.pkl")
print("   ✅ scaler_diet.pkl")
print("   ✅ features_diet.pkl")

# ══════════════════════════════════════════════════════
# ÉTAPE 10 — RAPPORT PIPELINE
# ══════════════════════════════════════════════════════
print("\n📄 ÉTAPE 10 — GÉNÉRATION DES RAPPORTS")
print("-" * 60)

duree = (datetime.now() - debut).seconds

rapport_path = os.path.join(RAPPORT_DIR, "rapport_rf_nutrition_final.md")
with open(rapport_path, "w", encoding="utf-8") as f:

    f.write("# Rapport Random Forest — Nutrition Final\n\n")
    f.write(f"**Projet** : HealthAI Coach — MSPR 2  \n")
    f.write(f"**Algorithme** : Random Forest  \n")
    f.write(f"**Compétences** : DIADS2.1, DIADS2.3, DIADS2.4, DIADS2.5, DIADS2.6  \n")
    f.write(f"**Généré le** : {datetime.now().strftime('%d/%m/%Y à %H:%M')}  \n")
    f.write(f"**Durée** : {duree}s  \n\n")
    f.write("---\n\n")

    f.write("## 1. Colonnes retirées\n\n")
    f.write("| Colonne | Raison |\n|---------|--------|\n")
    for col, raison in colonnes_retirees.items():
        f.write(f"| `{col}` | {raison} |\n")
    f.write("\n---\n\n")

    f.write("## 2. Features utilisées\n\n")
    f.write("| Feature | Type | Source | Description |\n")
    f.write("|---------|------|--------|-------------|\n")
    details = {
        'age':                    ('Numérique',    'Formulaire',    'Âge de l\'utilisateur en années'),
        'gender':                 ('Catégorielle', 'Formulaire',    'Genre : Female ou Male'),
        'weight_kg':              ('Numérique',    'Formulaire',    'Poids en kilogrammes'),
        'height_cm':              ('Numérique',    'Formulaire',    'Taille en centimètres'),
        'bmi':                    ('Numérique',    'Calculé auto',  'Indice de masse corporelle = poids/(taille²)'),
        'physical_activity_level':('Catégorielle', 'Formulaire',    'Niveau d\'activité : Active / Moderate / Sedentary'),
        'weekly_exercise_hours':  ('Numérique',    'Formulaire',    'Heures d\'exercice par semaine'),
        'daily_caloric_intake':   ('Numérique',    'Formulaire',    'Apport calorique journalier estimé'),
        'caloric_density':        ('Numérique',    'Calculé auto',  'Ratio calories/poids — mesure l\'apport calorique relatif'),
        'bmi_category':           ('Catégorielle', 'Calculé auto',  'Catégorie IMC : underweight/normal/overweight/obese'),
        'age_group':              ('Catégorielle', 'Calculé auto',  'Tranche d\'âge : young/adult/middle/senior'),
    }
    for feat in features:
        typ, src, desc = details[feat]
        f.write(f"| `{feat}` | {typ} | {src} | {desc} |\n")
    f.write("\n---\n\n")

    f.write("## 3. Résultats\n\n")
    f.write("| Métrique | RF Base | RF Optimisé |\n|----------|---------|-------------|\n")
    f.write(f"| Accuracy | {acc_base:.4f} | {acc_best:.4f} |\n")
    f.write(f"| F1-score | {f1_base:.4f} | {f1_best:.4f} |\n")
    f.write(f"| Precision | — | {pr_best:.4f} |\n")
    f.write(f"| Recall | — | {re_best:.4f} |\n")
    f.write(f"| CV F1 moyen | — | {cv_scores.mean():.4f} |\n\n")
    f.write(f"**Meilleurs paramètres** : `{grid.best_params_}`\n\n")
    f.write("```\n")
    f.write(classification_report(y_test, y_pred_best, target_names=le_target.classes_))
    f.write("```\n\n---\n\n")

    f.write("## 4. Top features\n\n")
    f.write("| Rang | Feature | Importance |\n|------|---------|------------|\n")
    for i, (feat, imp) in enumerate(feat_imp.head(5).items(), 1):
        f.write(f"| {i} | `{feat}` | {imp:.4f} |\n")
    f.write(f"\n*Rapport généré automatiquement — Durée : {duree}s*\n")

print(f"   ✅ {rapport_path}")

# ══════════════════════════════════════════════════════
# RAPPORT DE TEST ML
# ══════════════════════════════════════════════════════
rapport_test_path = os.path.join(RAPPORT_DIR, "rapport_test_ml_nutrition.md")
with open(rapport_test_path, "w", encoding="utf-8") as f:

    f.write("# Rapport de test ML — Recommandation Nutritionnelle\n\n")
    f.write(f"**Projet** : HealthAI Coach — MSPR 2  \n")
    f.write(f"**Généré le** : {datetime.now().strftime('%d/%m/%Y à %H:%M')}  \n\n")
    f.write("---\n\n")

    f.write("## 1. Contexte\n\n")
    f.write("Ce rapport documente l'ensemble des tests et expérimentations réalisés ")
    f.write("pour développer le modèle de recommandation nutritionnelle de HealthAI Coach. ")
    f.write("Il retrace les problématiques rencontrées, les décisions prises et justifie ")
    f.write("pourquoi le score final de 46% est le résultat honnête et défendable.\n\n")
    f.write("---\n\n")

    f.write("## 2. Problématique 1 — Score de 100% (data leakage)\n\n")
    f.write("### Symptôme\n\n")
    f.write("Lors des premiers tests, tous les algorithmes (Random Forest, Gradient Boosting, ")
    f.write("Decision Tree, KNN) donnaient un score de 100%. Un score parfait sur un dataset ")
    f.write("réel est systématiquement le signe d'un problème.\n\n")
    f.write("### Cause identifiée\n\n")
    f.write("Le dataset présente une corrélation parfaite entre `disease_type` et la cible :\n\n")
    f.write("| disease_type | diet_recommendation |\n|--------------|--------------------|\n")
    f.write("| Diabetes | Low_Carb |\n")
    f.write("| Hypertension | Low_Sodium |\n")
    f.write("| Obesity / None | Balanced |\n\n")
    f.write("C'est ce qu'on appelle le **data leakage** : une variable d'entrée qui contient ")
    f.write("directement la réponse. Le modèle apprend une règle triviale sans généralisation.\n\n")
    f.write("De plus, `dietary_restrictions`, `allergies` et `preferred_cuisine` étaient ")
    f.write("également corrélées à la cible et contribuaient au leakage.\n\n")
    f.write("### Solution appliquée\n\n")
    f.write("Suppression de toutes les colonnes causant le data leakage : `disease_type`, ")
    f.write("`severity`, `dietary_restrictions`, `allergies`, `preferred_cuisine`.\n\n")
    f.write("---\n\n")

    f.write("## 3. Problématique 2 — Choix des features accessibles\n\n")
    f.write("### Symptôme\n\n")
    f.write("Après suppression du data leakage, le score est descendu à ~46%. ")
    f.write("Des colonnes comme `cholesterol_mg/dl`, `blood_pressure_mmhg` et ")
    f.write("`glucose_mg/dl` étaient disponibles mais posaient un problème d'accessibilité.\n\n")
    f.write("### Problème\n\n")
    f.write("Ces données nécessitent des analyses médicales (prise de sang, tensiomètre) ")
    f.write("inaccessibles pour un utilisateur lambda qui remplit un formulaire dans une appli. ")
    f.write("Les utiliser aurait rendu le modèle inutilisable en production réelle.\n\n")
    f.write("### Solution appliquée\n\n")
    f.write("Limitation aux données qu'un utilisateur peut renseigner sans consultation médicale : ")
    f.write("âge, genre, poids, taille, niveau d'activité, heures d'exercice et apport calorique estimé. ")
    f.write("Les features calculées automatiquement (BMI, catégorie IMC, tranche d'âge, densité calorique) ")
    f.write("ont été ajoutées car elles sont dérivées des données déjà disponibles.\n\n")
    f.write("---\n\n")

    f.write("## 4. Problématique 3 — Ajout de features médicales optionnelles\n\n")
    f.write("### Test réalisé\n\n")
    f.write("Pour tenter d'atteindre un score de 70%, nous avons testé l'ajout de features ")
    f.write("médicales optionnelles : `cholesterol_mg/dl`, `blood_pressure_mmhg`, `glucose_mg/dl`, ")
    f.write("`adherence_to_diet_plan`, `dietary_nutrient_imbalance_score`.\n\n")
    f.write("### Résultat\n\n")
    f.write("Le score a **baissé** de 46% à 41%. L'ajout de ces colonnes a dégradé les performances.\n\n")
    f.write("### Explication\n\n")
    f.write("Deux raisons expliquent cette dégradation :\n\n")
    f.write("- `adherence_to_diet_plan` et `dietary_nutrient_imbalance_score` sont des colonnes ")
    f.write("subjectives et mal corrélées à la cible. Elles introduisent du bruit plutôt que du signal.\n")
    f.write("- Avec seulement 1000 lignes, l'ajout de features supplémentaires augmente la ")
    f.write("dimensionnalité sans apporter d'information discriminante, ce qui dilue le signal.\n\n")
    f.write("### Décision\n\n")
    f.write("Retour aux 11 features basiques qui donnent le meilleur score honnête.\n\n")
    f.write("---\n\n")

    f.write("## 5. Problématique 4 — Comparaison multi-algorithmes\n\n")
    f.write("### Tests réalisés\n\n")
    f.write("Quatre algorithmes ont été testés sur les mêmes features :\n\n")
    f.write("| Algorithme | Score approx | Observation |\n")
    f.write("|------------|-------------|-------------|\n")
    f.write("| Random Forest | ~46% | Meilleur score, robuste au déséquilibre |\n")
    f.write("| Gradient Boosting | ~44% | Similaire, plus lent à entraîner |\n")
    f.write("| Decision Tree | ~42% | Surapprentissage sur données peu nombreuses |\n")
    f.write("| KNN | ~40% | Sensible aux échelles, moins adapté |\n\n")
    f.write("### Conclusion\n\n")
    f.write("Tous les algorithmes donnent des scores similaires autour de 40-46%. ")
    f.write("Cela confirme que la limite vient **des données** et non de l'algorithme. ")
    f.write("Le Random Forest a été retenu comme meilleur choix.\n\n")
    f.write("---\n\n")

    f.write("## 6. Pourquoi on se contente de 46%\n\n")
    f.write("### Raison 1 — Nature du dataset\n\n")
    f.write("Le dataset `diet_recommendations` est un dataset synthétique Kaggle construit ")
    f.write("avec des règles simples. Une fois le data leakage corrigé, il ne reste que ")
    f.write("des données biométriques basiques sans corrélation forte avec les 3 régimes. ")
    f.write("Aucun algorithme ne peut extraire ce qui n'existe pas dans les données.\n\n")
    f.write("### Raison 2 — Cohérence avec la réalité\n\n")
    f.write("En réalité, prédire un régime diététique uniquement depuis l'âge, le poids ")
    f.write("et l'activité physique est une tâche difficile même pour un médecin. ")
    f.write("Un score de 46% est donc cohérent avec la complexité médicale du problème.\n\n")
    f.write("### Raison 3 — Honnêteté scientifique\n\n")
    f.write("Forcer un score plus élevé nécessiterait de réintroduire du data leakage, ")
    f.write("ce qui donnerait un modèle qui fonctionne sur le dataset de test mais ")
    f.write("serait inutilisable en production réelle. Un modèle honnête à 46% est ")
    f.write("préférable à un modèle qui 'triche' à 90%.\n\n")
    f.write("### Raison 4 — Perspective d'amélioration\n\n")
    f.write("En production avec HealthAI Coach, le modèle s'améliorerait naturellement avec :\n\n")
    f.write("- Des données réelles collectées auprès de vrais utilisateurs\n")
    f.write("- Un historique alimentaire détaillé via le journal de l'appli\n")
    f.write("- Des données biométriques continues via objets connectés (Premium+)\n")
    f.write("- Un volume de données bien supérieur à 1000 lignes\n\n")
    f.write("---\n\n")

    f.write("## 7. Détail des variables utilisées\n\n")
    f.write("### Variables d'entrée (features)\n\n")
    f.write("| Feature | Type | Source | Encodage | Description détaillée |\n")
    f.write("|---------|------|--------|----------|----------------------|\n")
    f.write("| `age` | Numérique | Formulaire | StandardScaler | Âge en années. Pertinent car les besoins nutritionnels varient selon l'âge |\n")
    f.write("| `gender` | Catégorielle | Formulaire | LabelEncoder (Female=0, Male=1) | Genre de l'utilisateur. Impact sur le métabolisme de base |\n")
    f.write("| `weight_kg` | Numérique | Formulaire | StandardScaler | Poids en kg. Base du calcul du BMI et de la densité calorique |\n")
    f.write("| `height_cm` | Numérique | Formulaire | StandardScaler | Taille en cm. Base du calcul du BMI |\n")
    f.write("| `bmi` | Numérique | Calculé auto | StandardScaler | Indice de masse corporelle = poids/(taille²). Indicateur de corpulence |\n")
    f.write("| `physical_activity_level` | Catégorielle | Formulaire | LabelEncoder (Active=0, Moderate=1, Sedentary=2) | Niveau d'activité. Impact direct sur les besoins caloriques |\n")
    f.write("| `weekly_exercise_hours` | Numérique | Formulaire | StandardScaler | Heures d'exercice par semaine. Complète physical_activity_level |\n")
    f.write("| `daily_caloric_intake` | Numérique | Formulaire | StandardScaler | Apport calorique journalier estimé. Signal fort pour la nutrition |\n")
    f.write("| `caloric_density` | Numérique | Calculé auto | StandardScaler | calories/poids. Mesure l'apport relatif au poids corporel |\n")
    f.write("| `bmi_category` | Catégorielle | Calculé auto | LabelEncoder | Catégorie clinique : underweight/normal/overweight/obese |\n")
    f.write("| `age_group` | Catégorielle | Calculé auto | LabelEncoder | Tranche d'âge : young(0-25)/adult(25-35)/middle(35-50)/senior(50+) |\n\n")

    f.write("### Variable cible\n\n")
    f.write("| Classe | Encodage | Effectif | Description |\n")
    f.write("|--------|----------|----------|-------------|\n")
    f.write("| Balanced | 0 | 426 (43%) | Régime équilibré — pas de restriction particulière |\n")
    f.write("| Low_Carb | 1 | 258 (26%) | Régime pauvre en glucides |\n")
    f.write("| Low_Sodium | 2 | 316 (32%) | Régime pauvre en sodium |\n\n")

    f.write("### Variables retirées\n\n")
    f.write("| Colonne | Catégorie | Raison détaillée |\n")
    f.write("|---------|-----------|------------------|\n")
    f.write("| `patient_id` | Technique | Identifiant sans valeur prédictive. Ferait mémoriser des cas spécifiques |\n")
    f.write("| `disease_type` | Data leakage | Corrélation parfaite 1:1 avec la cible. Donne 100% mais sans apprentissage réel |\n")
    f.write("| `severity` | Data leakage indirect | Liée à disease_type, contribue au leakage |\n")
    f.write("| `dietary_restrictions` | Data leakage | Low_Sodium dans restrictions → Low_Sodium recommandé |\n")
    f.write("| `allergies` | Data leakage | Corrélée à la cible |\n")
    f.write("| `preferred_cuisine` | Data leakage | Corrélée à la cible |\n")
    f.write("| `cholesterol_mg/dl` | Inaccessible | Nécessite prise de sang |\n")
    f.write("| `blood_pressure_mmhg` | Inaccessible | Nécessite tensiomètre |\n")
    f.write("| `glucose_mg/dl` | Inaccessible | Nécessite analyse sanguine |\n")
    f.write("| `adherence_to_diet_plan` | Dégradant | Subjectif, dégrade les performances |\n")
    f.write("| `dietary_nutrient_imbalance_score` | Dégradant | Score professionnel, dégrade les performances |\n\n")

    f.write("---\n\n")
    f.write("## 8. Résultats finaux\n\n")
    f.write(f"| Métrique | RF Base | RF Optimisé |\n|----------|---------|-------------|\n")
    f.write(f"| Accuracy | {acc_base:.4f} | {acc_best:.4f} |\n")
    f.write(f"| F1-score | {f1_base:.4f} | {f1_best:.4f} |\n")
    f.write(f"| Precision | — | {pr_best:.4f} |\n")
    f.write(f"| Recall | — | {re_best:.4f} |\n")
    f.write(f"| CV F1 moyen | — | {cv_scores.mean():.4f} |\n\n")
    f.write("```\n")
    f.write(classification_report(y_test, y_pred_best, target_names=le_target.classes_))
    f.write("```\n\n")
    f.write("---\n\n")
    f.write(f"*Rapport généré automatiquement — Durée totale : {duree}s*\n")

print(f"   ✅ {rapport_test_path}")

# ══════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ══════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PIPELINE FINAL TERMINÉ")
print("=" * 60)
print(f"Durée              : {duree} secondes")
print(f"Features utilisées : {len(features)}")
print(f"Colonnes retirées  : {len(colonnes_retirees)}")
print(f"Accuracy           : {acc_best:.4f}")
print(f"F1-score           : {f1_best:.4f}")
print(f"CV F1 moyen        : {cv_scores.mean():.4f}")
print(f"Classes prédites   : {list(le_target.classes_)}")
print()
print("Fichiers générés :")
print("  data/clean_ml/diet_recommendations_ml.csv")
print("  models/model_nutrition.pkl")
print("  outputs/confusion_matrix_nutrition_final.png")
print("  outputs/feature_importance_nutrition_final.png")
print("  outputs/comparaison_rf_nutrition_final.png")
print("  outputs/distribution_cible_nutrition_final.png")
print("  rapport/rapport_rf_nutrition_final.md")
print("  rapport/rapport_test_ml_nutrition.md")
print("=" * 60)