# Rapport Random Forest — Niveau Expérience Fitness (Final)

**Projet** : HealthAI Coach — MSPR 2  
**Algorithme** : Random Forest (classification supervisée)  
**Cible** : `experience_level` (1=Débutant / 2=Intermédiaire / 3=Avancé)  
**Compétences** : DIADS2.1, DIADS2.3, DIADS2.4, DIADS2.5, DIADS2.6  
**Généré le** : 17/05/2026 à 10:48  
**Durée** : 30s  

---

## 1. Justification du choix

### Pourquoi experience_level et pas workout_type ?

Une première tentative sur `workout_type` avec 4 algorithmes a donné :

| Algorithme | Accuracy |
|------------|----------|
| Random Forest | 23% |
| Gradient Boosting | 19% |
| SVM | 25% |
| MLP | 21% |

Tous sous le hasard (25% sur 4 classes). Le dataset ne contient pas de corrélation entre données biométriques et type d'entraînement.

### Pourquoi workout_type est retiré des features ?

Dans le flux de l'application, `workout_type` est ce qu'on recommande **après** avoir déterminé le niveau. L'utiliser comme input créerait une incohérence logique : on ne peut pas demander à l'utilisateur quel exercice il fait pour lui recommander quel exercice faire.

```
Profil biométrique utilisateur
      ↓
Modèle prédit experience_level
      ↓
Débutant  → Cardio léger + Yoga
Intermédiaire → Strength + Cardio modéré
Avancé    → HIIT + Strength intense
      ↓
ExerciseDB MongoDB fournit les exercices concrets
```

---

## 2. Colonnes retirées

| Colonne | Raison |
|---------|--------|
| `workout_type` | C'est ce qu'on recommande après — pas une entrée utilisateur |
| `experience_level` | Variable cible — ne peut pas être une feature |

---

## 3. Features utilisées

| Feature | Type | Description |
|---------|------|-------------|
| `age` | Numérique | Âge en années |
| `gender` | Catégorielle | Genre (Female=0, Male=1) |
| `weight_kg` | Numérique | Poids en kg |
| `height_m` | Numérique | Taille en mètres |
| `bmi` | Numérique | Indice de masse corporelle |
| `max_bpm` | Numérique | BPM maximal — capacité cardiaque |
| `avg_bpm` | Numérique | BPM moyen pendant l'effort |
| `resting_bpm` | Numérique | BPM au repos — forme cardiovasculaire |
| `session_duration_hours` | Numérique | Durée de séance en heures |
| `calories_burned` | Numérique | Calories brûlées par séance |
| `fat_percentage` | Numérique | % graisse corporelle |
| `water_intake_liters` | Numérique | Consommation eau journalière |
| `workout_frequency_days/week` | Numérique | Fréquence d'entraînement/semaine |

---

## 4. Résultats (DIADS2.5)

| Métrique | RF Base | RF Optimisé |
|----------|---------|-------------|
| Accuracy | 0.8974 | 0.9077 |
| F1-score | 0.8971 | 0.9074 |
| Precision | — | 0.9092 |
| Recall | — | 0.9077 |
| CV F1 moyen | — | 0.8885 |

**Meilleurs paramètres** : `{'max_depth': None, 'min_samples_leaf': 1, 'min_samples_split': 5, 'n_estimators': 100}`

### Rapport de classification

```
               precision    recall  f1-score   support

     Débutant       0.91      0.84      0.88        75
Intermédiaire       0.86      0.93      0.89        82
       Avancé       1.00      1.00      1.00        38

     accuracy                           0.91       195
    macro avg       0.93      0.92      0.92       195
 weighted avg       0.91      0.91      0.91       195
```

---

## 5. Top features

| Rang | Feature | Importance |
|------|---------|------------|
| 1 | `session_duration_hours` | 0.2525 |
| 2 | `workout_frequency_days/week` | 0.2315 |
| 3 | `fat_percentage` | 0.1805 |
| 4 | `calories_burned` | 0.1171 |
| 5 | `water_intake_liters` | 0.0445 |

---

## 6. Conclusion

Le modèle atteint **90.77% d'accuracy** et **90.74% de F1-score**, bien au-dessus de l'objectif de 70%.

- **Cible pertinente** : experience_level conditionne le programme
- **workout_type retiré** : c'est la sortie du système pas l'entrée
- **Score excellent** : >89% F1-score
- **Aligné CDC** : progression actuelle et niveau de forme
- **Prêt pour l'API** : modèles sauvegardés en `.pkl`

*Généré automatiquement — Durée : 30s*
