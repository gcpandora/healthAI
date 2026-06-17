# Rapport Random Forest — Nutrition Final

**Projet** : HealthAI Coach — MSPR 2  
**Algorithme** : Random Forest  
**Compétences** : DIADS2.1, DIADS2.3, DIADS2.4, DIADS2.5, DIADS2.6  
**Généré le** : 17/05/2026 à 10:40  
**Durée** : 74s  

---

## 1. Colonnes retirées

| Colonne | Raison |
|---------|--------|
| `patient_id` | Identifiant technique inutile pour le ML |
| `disease_type` | Data leakage — corrélation parfaite avec la cible |
| `severity` | Liée à disease_type — data leakage indirect |
| `dietary_restrictions` | Data leakage — corrélée à la cible |
| `allergies` | Data leakage — corrélée à la cible |
| `preferred_cuisine` | Data leakage — corrélée à la cible |
| `cholesterol_mg/dl` | Nécessite prise de sang — inaccessible utilisateur lambda |
| `blood_pressure_mmhg` | Nécessite tensiomètre — inaccessible utilisateur lambda |
| `glucose_mg/dl` | Nécessite analyse sanguine — inaccessible utilisateur lambda |
| `adherence_to_diet_plan` | Donnée subjective — dégrade les performances |
| `dietary_nutrient_imbalance_score` | Calculé par professionnel — dégrade les performances |

---

## 2. Features utilisées

| Feature | Type | Source | Description |
|---------|------|--------|-------------|
| `age` | Numérique | Formulaire | Âge de l'utilisateur en années |
| `gender` | Catégorielle | Formulaire | Genre : Female ou Male |
| `weight_kg` | Numérique | Formulaire | Poids en kilogrammes |
| `height_cm` | Numérique | Formulaire | Taille en centimètres |
| `bmi` | Numérique | Calculé auto | Indice de masse corporelle = poids/(taille²) |
| `physical_activity_level` | Catégorielle | Formulaire | Niveau d'activité : Active / Moderate / Sedentary |
| `weekly_exercise_hours` | Numérique | Formulaire | Heures d'exercice par semaine |
| `daily_caloric_intake` | Numérique | Formulaire | Apport calorique journalier estimé |
| `caloric_density` | Numérique | Calculé auto | Ratio calories/poids — mesure l'apport calorique relatif |
| `bmi_category` | Catégorielle | Calculé auto | Catégorie IMC : underweight/normal/overweight/obese |
| `age_group` | Catégorielle | Calculé auto | Tranche d'âge : young/adult/middle/senior |

---

## 3. Résultats

| Métrique | RF Base | RF Optimisé |
|----------|---------|-------------|
| Accuracy | 0.4450 | 0.4400 |
| F1-score | 0.4043 | 0.4255 |
| Precision | — | 0.4179 |
| Recall | — | 0.4400 |
| CV F1 moyen | — | 0.3717 |

**Meilleurs paramètres** : `{'class_weight': 'balanced', 'max_depth': 20, 'min_samples_leaf': 1, 'min_samples_split': 10, 'n_estimators': 300}`

```
              precision    recall  f1-score   support

    Balanced       0.51      0.56      0.53        85
    Low_Carb       0.24      0.15      0.19        52
  Low_Sodium       0.45      0.51      0.48        63

    accuracy                           0.44       200
   macro avg       0.40      0.41      0.40       200
weighted avg       0.42      0.44      0.43       200
```

---

## 4. Top features

| Rang | Feature | Importance |
|------|---------|------------|
| 1 | `daily_caloric_intake` | 0.1398 |
| 2 | `bmi` | 0.1373 |
| 3 | `weekly_exercise_hours` | 0.1368 |
| 4 | `caloric_density` | 0.1308 |
| 5 | `weight_kg` | 0.1284 |

*Rapport généré automatiquement — Durée : 74s*
