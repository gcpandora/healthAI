# Sources de données — HealthAI Coach

## Justification du choix des datasets

### Dataset 1 : Daily Food & Nutrition Dataset (Kaggle)

**URL :** https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset
**Format :** CSV
**Volume estimé :** ~500-1000 entrées alimentaires

**Justification :**
Ce dataset couvre directement le besoin de base nutritionnelle du cahier des charges. Il fournit
les valeurs énergétiques et macronutriments (protéines, glucides, lipides) nécessaires au moteur
de recommandation nutritionnelle. Il est en open data, bien structuré et documenté.

**Règles de qualité appliquées :**
- Suppression des lignes avec valeurs nutritionnelles nulles ou négatives
- Normalisation des unités (tout en grammes/100g)
- Déduplication sur le nom de l'aliment
- Encodage UTF-8 forcé (caractères spéciaux dans les noms d'aliments)

---

### Dataset 2 : Gym Members Exercise Dataset (Kaggle)

**URL :** https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset
**Format :** CSV
**Volume estimé :** 973 échantillons

**Justification :**
Ce dataset fournit les profils utilisateurs fictifs avec données démographiques (âge, genre, poids,
taille) et métriques biométriques (BPM, calories, BMI, % graisse corporelle). Il correspond
exactement aux données utilisateurs décrites dans le cahier des charges.

**Règles de qualité appliquées :**
- Vérification des plages valides (âge 10-100, poids 30-300kg, taille 100-250cm)
- Imputation des valeurs manquantes par la médiane du groupe (genre + tranche d'âge)
- Anonymisation complète (aucune donnée personnelle réelle)
- Calcul du BMI recalculé et vérifié (cohérence poids/taille/IMC déclaré)

---

## Schéma des flux de données (vue simplifiée)

```
[Kaggle CSV]        [ExerciseDB JSON]
      │                     │
      ▼                     ▼
 [Extract]            [Extract]
      │                     │
      ▼                     ▼
 [Transform]          [Transform]
   nettoyage            parsing
   validation           mapping
      │                     │
      └──────────┬──────────┘
                 ▼
          [PostgreSQL]
          healthai_db
                 │
         ┌───────┼───────┐
         ▼       ▼       ▼
      [API]  [Metabase] [ML]
```

## Fréquence de mise à jour

| Source | Fréquence | Méthode |
|--------|-----------|---------|
| Nutrition (Kaggle) | À la demande | Script manuel ou cron mensuel |
| Profils utilisateurs (Kaggle) | Unique (seed) | Script d'initialisation |
| Exercices (ExerciseDB) | Trimestriel | Script automatisé |
