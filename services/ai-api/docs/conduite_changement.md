# Conduite du changement — HealthAI Coach API IA
## MSPR TPRE502 — Accessibilité WCAG/RGAA AA et adoption utilisateurs

---

## 1. Contexte

L'introduction de l'API IA dans HealthAI Coach représente un changement majeur pour deux populations :
- **Les utilisateurs finaux** : nouvelles fonctionnalités (analyse photo, plans personnalisés)
- **L'équipe technique** : intégration d'un LLM local et d'une API cloud dans l'architecture existante

---

## 2. Analyse des parties prenantes

| Partie prenante | Impact | Résistance estimée | Stratégie |
|---|---|---|---|
| Utilisateurs Premium | Fort (nouvelles fonctions) | Faible (valeur perçue élevée) | Communication, tutoriels |
| Utilisateurs Freemium | Moyen (accès limité) | Moyenne (frustration possible) | Clarifier les limites gratuites |
| Équipe frontend | Fort (nouveaux endpoints) | Faible (doc OpenAPI fournie) | Formation, Swagger UI |
| Équipe DevOps | Moyen (Ollama à déployer) | Faible | Documentation Docker |
| DPO / Juridique | Fort (données santé) | Potentiellement forte | Argument RGPD Ollama local |

---

## 3. Accessibilité — Conformité WCAG 2.1 AA / RGAA 4.1

### 3.1 Périmètre d'application

Les fonctionnalités IA ajoutent des interfaces spécifiques qui doivent respecter le niveau AA :
- Formulaire d'upload de photo de repas
- Affichage des résultats d'analyse nutritionnelle
- Visualisation du plan de repas (tableaux)
- Affichage du programme d'entraînement

### 3.2 Critères WCAG AA appliqués par fonctionnalité

#### Upload photo (`POST /nutrition/analyze`)

| Critère | Implémentation |
|---|---|
| 1.1.1 Contenu non textuel | `alt` descriptif sur l'aperçu de la photo uploadée |
| 1.4.3 Contraste | Bouton upload : ratio ≥ 4.5:1 vérifié |
| 2.1.1 Accessibilité clavier | Upload déclenché par Entrée/Espace |
| 3.3.1 Identification des erreurs | Message explicite si format invalide ("Seuls JPEG/PNG sont acceptés") |
| 4.1.2 Nom, rôle, valeur | `<input type="file" aria-label="Photo de votre repas">` |

#### Résultats d'analyse nutritionnelle

| Critère | Implémentation |
|---|---|
| 1.3.1 Information et relations | Score santé affiché avec texte + couleur (pas uniquement couleur) |
| 1.4.1 Utilisation de la couleur | Score 1-10 affiché avec icône + texte en plus de la couleur |
| 2.4.6 En-têtes et étiquettes | `<h2>Aliments détectés</h2>`, `<h2>Valeurs nutritionnelles</h2>` |
| 3.1.1 Langue de la page | `<html lang="fr">` |

#### Tableaux (plan de repas, programme sport)

| Critère | Implémentation |
|---|---|
| 1.3.1 Information et relations | `<table>` avec `<thead>`, `<th scope="col/row">` |
| 2.4.6 Étiquettes descriptives | Caption sur chaque tableau |

### 3.3 Tests d'accessibilité planifiés

| Outil | Usage | Fréquence |
|---|---|---|
| axe DevTools | Audit automatisé Chrome | À chaque PR |
| NVDA + Chrome | Test lecteur d'écran | Sprint review |
| Contrast Checker | Vérification ratios couleurs | À chaque nouvelle couleur |
| Clavier seul | Navigation sans souris | Sprint review |

---

## 4. Plan d'adoption utilisateurs

### 4.1 Phase 1 — Lancement Beta (semaines 1-2)

**Objectif** : valider l'expérience utilisateur avec un groupe restreint.

- Sélection de 50 utilisateurs Premium volontaires
- Accès aux 3 nouvelles fonctionnalités IA
- Formulaire de feedback intégré à chaque résultat IA
- Indicateur de source visible ("Généré par IA — peut contenir des erreurs")

**Métriques de succès** :
- Taux d'utilisation > 60% des beta testeurs
- Note moyenne satisfaction ≥ 3.5/5
- Taux d'erreur API < 5%

### 4.2 Phase 2 — Déploiement progressif (semaines 3-4)

- Activation pour 30% des utilisateurs Premium
- Monitoring des performances Ollama (latence, disponibilité)
- Ajustement des prompts selon les retours qualité

### 4.3 Phase 3 — Déploiement complet (semaine 5+)

- Activation pour tous les utilisateurs Premium
- Communication in-app (notification push, bannière)
- Documentation utilisateur (FAQ, vidéo tutoriel 2min)

---

## 5. Communication

### 5.1 Messages clés par audience

**Utilisateurs Premium :**
> "Votre coach IA personnel est arrivé. Analysez vos repas en photo, obtenez un plan nutritionnel sur mesure et un programme sportif adapté à votre niveau — tout en gardant vos données médicales confidentielles sur nos serveurs."

**Équipe technique :**
> "L'API IA est documentée sur Swagger UI (http://localhost:8002/docs). Le service Ollama tourne localement — aucune donnée de santé ne quitte l'infrastructure. En cas d'indisponibilité, le fallback garantit la continuité de service."

### 5.2 Canaux de communication

| Canal | Audience | Contenu |
|---|---|---|
| In-app notification | Utilisateurs Premium | Annonce nouvelles fonctions |
| Email onboarding | Nouveaux inscrits Premium | Guide démarrage rapide |
| Swagger UI `/docs` | Développeurs frontend | Documentation technique |
| README Docker | DevOps | Déploiement Ollama |

---

## 6. Gestion des risques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Ollama trop lent (CPU sans GPU) | Élevée | Moyen | Afficher un loader + message "Analyse en cours (8-15s)" |
| Réponse IA incorrecte (hallucination) | Moyenne | Élevé | Disclaimer visible : "Consultez un professionnel de santé" |
| HuggingFace quota épuisé | Faible | Faible | Fallback sur description texte automatique |
| Résistance RGPD (données cloud HF) | Faible | Élevé | Seules les photos transitent — pas les données médicales |

---

## 7. Indicateurs de succès (KPIs)

| KPI | Cible | Mesure |
|---|---|---|
| Taux d'adoption fonction analyse photo | > 40% utilisateurs Premium/mois | Analytics in-app |
| Satisfaction fonctions IA | ≥ 4/5 | Note post-utilisation |
| Disponibilité API IA | ≥ 99% | `GET /health` monitoring |
| Temps de réponse moyen | < 10s (P95) | Logs Uvicorn |
| Taux fallback activé | < 5% | Logs source="fallback" |
