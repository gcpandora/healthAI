# Rapport de test ML — Recommandation Nutritionnelle

**Projet** : HealthAI Coach — MSPR 2  
**Généré le** : 17/05/2026 à 10:40  

---

## 1. Contexte

Ce rapport documente l'ensemble des tests et expérimentations réalisés pour développer le modèle de recommandation nutritionnelle de HealthAI Coach. Il retrace les problématiques rencontrées, les décisions prises et justifie pourquoi le score final de 46% est le résultat honnête et défendable.

---

## 2. Problématique 1 — Score de 100% (data leakage)

### Symptôme

Lors des premiers tests, tous les algorithmes (Random Forest, Gradient Boosting, Decision Tree, KNN) donnaient un score de 100%. Un score parfait sur un dataset réel est systématiquement le signe d'un problème.

### Cause identifiée

Le dataset présente une corrélation parfaite entre `disease_type` et la cible :

| disease_type | diet_recommendation |
|--------------|--------------------|
| Diabetes | Low_Carb |
| Hypertension | Low_Sodium |
| Obesity / None | Balanced |

C'est ce qu'on appelle le **data leakage** : une variable d'entrée qui contient directement la réponse. Le modèle apprend une règle triviale sans généralisation.

De plus, `dietary_restrictions`, `allergies` et `preferred_cuisine` étaient également corrélées à la cible et contribuaient au leakage.

### Solution appliquée

Suppression de toutes les colonnes causant le data leakage : `disease_type`, `severity`, `dietary_restrictions`, `allergies`, `preferred_cuisine`.

---

## 3. Problématique 2 — Choix des features accessibles

### Symptôme

Après suppression du data leakage, le score est descendu à ~46%. Des colonnes comme `cholesterol_mg/dl`, `blood_pressure_mmhg` et `glucose_mg/dl` étaient disponibles mais posaient un problème d'accessibilité.

### Problème

Ces données nécessitent des analyses médicales (prise de sang, tensiomètre) inaccessibles pour un utilisateur lambda qui remplit un formulaire dans une appli. Les utiliser aurait rendu le modèle inutilisable en production réelle.

### Solution appliquée

Limitation aux données qu'un utilisateur peut renseigner sans consultation médicale : âge, genre, poids, taille, niveau d'activité, heures d'exercice et apport calorique estimé. Les features calculées automatiquement (BMI, catégorie IMC, tranche d'âge, densité calorique) ont été ajoutées car elles sont dérivées des données déjà disponibles.

---

## 4. Problématique 3 — Ajout de features médicales optionnelles

### Test réalisé

Pour tenter d'atteindre un score de 70%, nous avons testé l'ajout de features médicales optionnelles : `cholesterol_mg/dl`, `blood_pressure_mmhg`, `glucose_mg/dl`, `adherence_to_diet_plan`, `dietary_nutrient_imbalance_score`.

### Résultat

Le score a **baissé** de 46% à 41%. L'ajout de ces colonnes a dégradé les performances.

### Explication

Deux raisons expliquent cette dégradation :

- `adherence_to_diet_plan` et `dietary_nutrient_imbalance_score` sont des colonnes subjectives et mal corrélées à la cible. Elles introduisent du bruit plutôt que du signal.
- Avec seulement 1000 lignes, l'ajout de features supplémentaires augmente la dimensionnalité sans apporter d'information discriminante, ce qui dilue le signal.

### Décision

Retour aux 11 features basiques qui donnent le meilleur score honnête.

---

## 5. Problématique 4 — Comparaison multi-algorithmes

### Tests réalisés

Quatre algorithmes ont été testés sur les mêmes features :

| Algorithme | Score approx | Observation |
|------------|-------------|-------------|
| Random Forest | ~46% | Meilleur score, robuste au déséquilibre |
| Gradient Boosting | ~44% | Similaire, plus lent à entraîner |
| Decision Tree | ~42% | Surapprentissage sur données peu nombreuses |
| KNN | ~40% | Sensible aux échelles, moins adapté |

### Conclusion

Tous les algorithmes donnent des scores similaires autour de 40-46%. Cela confirme que la limite vient **des données** et non de l'algorithme. Le Random Forest a été retenu comme meilleur choix.

---

## 6. Pourquoi on se contente de 46%

### Raison 1 — Nature du dataset

Le dataset `diet_recommendations` est un dataset synthétique Kaggle construit avec des règles simples. Une fois le data leakage corrigé, il ne reste que des données biométriques basiques sans corrélation forte avec les 3 régimes. Aucun algorithme ne peut extraire ce qui n'existe pas dans les données.

### Raison 2 — Cohérence avec la réalité

En réalité, prédire un régime diététique uniquement depuis l'âge, le poids et l'activité physique est une tâche difficile même pour un médecin. Un score de 46% est donc cohérent avec la complexité médicale du problème.

### Raison 3 — Honnêteté scientifique

Forcer un score plus élevé nécessiterait de réintroduire du data leakage, ce qui donnerait un modèle qui fonctionne sur le dataset de test mais serait inutilisable en production réelle. Un modèle honnête à 46% est préférable à un modèle qui 'triche' à 90%.

### Raison 4 — Perspective d'amélioration

En production avec HealthAI Coach, le modèle s'améliorerait naturellement avec :

- Des données réelles collectées auprès de vrais utilisateurs
- Un historique alimentaire détaillé via le journal de l'appli
- Des données biométriques continues via objets connectés (Premium+)
- Un volume de données bien supérieur à 1000 lignes

---

## 7. Détail des variables utilisées

### Variables d'entrée (features)

| Feature | Type | Source | Encodage | Description détaillée |
|---------|------|--------|----------|----------------------|
| `age` | Numérique | Formulaire | StandardScaler | Âge en années. Pertinent car les besoins nutritionnels varient selon l'âge |
| `gender` | Catégorielle | Formulaire | LabelEncoder (Female=0, Male=1) | Genre de l'utilisateur. Impact sur le métabolisme de base |
| `weight_kg` | Numérique | Formulaire | StandardScaler | Poids en kg. Base du calcul du BMI et de la densité calorique |
| `height_cm` | Numérique | Formulaire | StandardScaler | Taille en cm. Base du calcul du BMI |
| `bmi` | Numérique | Calculé auto | StandardScaler | Indice de masse corporelle = poids/(taille²). Indicateur de corpulence |
| `physical_activity_level` | Catégorielle | Formulaire | LabelEncoder (Active=0, Moderate=1, Sedentary=2) | Niveau d'activité. Impact direct sur les besoins caloriques |
| `weekly_exercise_hours` | Numérique | Formulaire | StandardScaler | Heures d'exercice par semaine. Complète physical_activity_level |
| `daily_caloric_intake` | Numérique | Formulaire | StandardScaler | Apport calorique journalier estimé. Signal fort pour la nutrition |
| `caloric_density` | Numérique | Calculé auto | StandardScaler | calories/poids. Mesure l'apport relatif au poids corporel |
| `bmi_category` | Catégorielle | Calculé auto | LabelEncoder | Catégorie clinique : underweight/normal/overweight/obese |
| `age_group` | Catégorielle | Calculé auto | LabelEncoder | Tranche d'âge : young(0-25)/adult(25-35)/middle(35-50)/senior(50+) |

### Variable cible

| Classe | Encodage | Effectif | Description |
|--------|----------|----------|-------------|
| Balanced | 0 | 426 (43%) | Régime équilibré — pas de restriction particulière |
| Low_Carb | 1 | 258 (26%) | Régime pauvre en glucides |
| Low_Sodium | 2 | 316 (32%) | Régime pauvre en sodium |

### Variables retirées

| Colonne | Catégorie | Raison détaillée |
|---------|-----------|------------------|
| `patient_id` | Technique | Identifiant sans valeur prédictive. Ferait mémoriser des cas spécifiques |
| `disease_type` | Data leakage | Corrélation parfaite 1:1 avec la cible. Donne 100% mais sans apprentissage réel |
| `severity` | Data leakage indirect | Liée à disease_type, contribue au leakage |
| `dietary_restrictions` | Data leakage | Low_Sodium dans restrictions → Low_Sodium recommandé |
| `allergies` | Data leakage | Corrélée à la cible |
| `preferred_cuisine` | Data leakage | Corrélée à la cible |
| `cholesterol_mg/dl` | Inaccessible | Nécessite prise de sang |
| `blood_pressure_mmhg` | Inaccessible | Nécessite tensiomètre |
| `glucose_mg/dl` | Inaccessible | Nécessite analyse sanguine |
| `adherence_to_diet_plan` | Dégradant | Subjectif, dégrade les performances |
| `dietary_nutrient_imbalance_score` | Dégradant | Score professionnel, dégrade les performances |

---

## 8. Résultats finaux

| Métrique | RF Base | RF Optimisé |
|----------|---------|-------------|
| Accuracy | 0.4450 | 0.4400 |
| F1-score | 0.4043 | 0.4255 |
| Precision | — | 0.4179 |
| Recall | — | 0.4400 |
| CV F1 moyen | — | 0.3717 |

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

*Rapport généré automatiquement — Durée totale : 74s*
