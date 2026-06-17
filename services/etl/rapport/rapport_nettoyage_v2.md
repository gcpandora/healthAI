# Rapport de nettoyage des données

**Projet** : HealthAI Coach — Backend Métier  
**Généré le** : 30/04/2026 à 13:55  

---

## Stratégie de nettoyage

| Destination | Stratégie |
|-------------|----------|
| BDD | Suppression doublons, correction types, NULL conservés, colonnes mappées vers schéma SQL |
| Machine Learning | Suppression NULL, encodage texte, normalisation StandardScaler |

---

## Bilan BDD

| Dataset | Table cible | Lignes | Actions |
|---------|-------------|--------|---------|
| daily_food_nutrition  | nutrition_items  | 591 | Doublons supprimés, colonnes renommées |
| diet_recommendations  | health_profiles  | 1000 | Colonnes mappées, severity/activity normalisés |
| gym_members_exercise  | users + user_metrics | 973 | Colonnes normalisées |
| gym_members_synthetic | users + user_metrics | 1800 | Max_BPM corrigé |

---

## Bilan Machine Learning

| Dataset | Lignes après nettoyage | Actions |
|---------|------------------------|--------|
| daily_food_nutrition  | 591 | NULL supprimés, encodage, normalisation |
| diet_recommendations  | 1000 | NULL remplis/supprimés, encodage, normalisation |
| gym_members_exercise  | 973 | NULL supprimés, encodage, normalisation |
| gym_members_synthetic | 1352 | NULL supprimés, encodage, normalisation |
