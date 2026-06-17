# Accessibilité et Conduite du Changement — HealthAI Coach

**Projet :** HealthAI Coach — MSPR TPRE502  
**Date :** Mai 2026  
**Référentiels :** WCAG 2.1 niveau AA, RGAA 4.1

---

## Partie 1 — Choix d'accessibilité techniques

### Principes directeurs

L'application HealthAI Coach dessert des utilisateurs aux profils variés — incluant des personnes souffrant de pathologies chroniques documentées dans `health_profiles` — ce qui impose un niveau d'accessibilité minimum conforme WCAG 2.1 AA et RGAA 4.1. Les choix techniques d'accessibilité ont été intégrés dès la conception des wireframes et implémentés dans les composants React.

### Attributs ARIA et sémantique

**`aria-live` et `role="status"` / `role="alert"`**

Les zones de résultat dynamiques utilisent `aria-live="polite"` pour les mises à jour non urgentes (chargement des recommandations fitness dans `docs/maquettes/06-fitness-resultat.html`) et `role="alert"` pour les messages d'erreur critiques (service indisponible, rate limiting 429 dans `docs/maquettes/04-nutrition-degrade.html`). Ce double dispositif garantit que les lecteurs d'écran (NVDA, VoiceOver) annoncent les changements de contenu sans interrompre la navigation.

**`aria-busy`**

Les états de chargement intermédiaires exposent `aria-busy="true"` sur le conteneur principal pendant les appels à l'endpoint `POST /api/v1/vision/analyze-meal`. L'attribut passe à `false` à la réception de la réponse, qu'il s'agisse d'un résultat IA ou d'un fallback. Ce comportement est représenté dans le wireframe `docs/maquettes/07-fitness-skeleton.html`.

**`fieldset` + `legend`**

Les formulaires de saisie (upload photo repas, formulaire profil fitness dans `docs/maquettes/02-nutrition-upload.html` et `docs/maquettes/05-fitness-formulaire.html`) groupent les champs liés via `<fieldset>` et `<legend>` explicite. Cette structure est lue par les technologies d'assistance comme un groupe logique avant chaque champ, supprimant toute ambiguïté sur le contexte de saisie.

**Focus outline et navigation clavier**

Un contour de focus visible (`outline: 3px solid #0066CC; outline-offset: 2px`) est appliqué sur tous les éléments interactifs, en remplacement du comportement par défaut souvent masqué par les feuilles de style. Le fichier `docs/maquettes/_shared.css` définit ce style globalement pour l'ensemble des wireframes. La navigation Tab/Shift+Tab suit l'ordre de lecture logique du DOM sur toutes les pages.

**Double codage couleur + icône + texte**

Les indicateurs d'état (succès, avertissement, erreur) ne reposent jamais sur la couleur seule. Chaque état combine : une couleur sémantique (vert/orange/rouge), une icône vectorielle (✓ / ⚠ / ✗), et un libellé textuel explicite. Ce triple codage respecte le critère WCAG 1.4.1 (Utilisation de la couleur) et est visible dans les wireframes `docs/maquettes/03-nutrition-resultat.html` et `docs/maquettes/04-nutrition-degrade.html`.

**Skeleton loaders informatifs**

Le wireframe `docs/maquettes/07-fitness-skeleton.html` implémente des squelettes de chargement accompagnés de `aria-label="Chargement des recommandations en cours"` sur le conteneur, permettant aux utilisateurs d'outils d'assistance d'identifier l'état d'attente plutôt que de recevoir un silence ou un contenu partiel.

---

## Partie 2 — Gestion de la robustesse pour l'accessibilité

### Principe : aucune perte silencieuse d'information

La robustesse d'une interface accessible repose sur la règle qu'un utilisateur utilisant un lecteur d'écran ou un outil de navigation clavier doit recevoir exactement la même information qu'un utilisateur voyant — y compris en cas de dégradation de service.

### Fallback du service Vision IA

Lorsque l'endpoint `POST /api/v1/vision/analyze-meal` déclenche le fallback (ai-api injoignable, timeout 30 s, ou erreur HTTP), la réponse retourne systématiquement un objet `MealAnalysisResponse` complet avec `is_fallback: true` et un champ `message` explicite. Le frontend interprète ce flag pour afficher un message visible et annoncé via `role="alert"` :

> "Analyse IA indisponible — estimations génériques affichées."

Ce message est lisible par lecteur d'écran, accompagné d'un indicateur visuel (icône ⚠ + fond orangé), et précède les données estimatives affichées. L'utilisateur sait ainsi qu'il consulte une estimation, non une analyse réelle. Ce comportement est illustré dans `docs/maquettes/04-nutrition-degrade.html`.

### Indisponibilité MongoDB (micro-service recommandation)

Le micro-service `recommendation` (port 8001) accède à MongoDB pour persister et récupérer les recommandations fitness. En cas d'indisponibilité de MongoDB, le service retourne une réponse dégradée avec un jeu de recommandations génériques. Le frontend (`FitnessRecommendations.jsx`) affiche ces recommandations avec un bandeau `role="status"` indiquant l'origine dégradée des données. Aucun composant ne reste en état vide ou "loading infini" — le skeleton loader de `docs/maquettes/07-fitness-skeleton.html` est toujours résolu, positivement ou en mode dégradé.

### Rate limiting HTTP 429

Le vision router impose une limite de 10 analyses par heure par adresse IP (`RATE_LIMIT = 10`, `RATE_WINDOW = 3600` dans `services/api/routers/vision_router.py`). Lorsque cette limite est atteinte, l'API retourne un HTTP 429 avec le message : *"Limite de 10 analyses par heure atteinte. Réessayez plus tard."* Le frontend intercepte ce code et affiche un message `role="alert"` avec un texte explicite incluant le délai de réinitialisation. L'état est communiqué via le header `X-RateLimit-Remaining` exposé à chaque réponse réussie, permettant d'afficher proactivement le nombre d'analyses restantes dans l'interface.

---

## Partie 3 — Conduite du changement

### Utilisateur non-technicien

L'utilisateur type d'HealthAI Coach n'a pas de formation en nutrition ou en fitness. La conduite du changement pour ce profil repose sur trois leviers :

**Simplicité du parcours principal.** Le dashboard (`docs/maquettes/01-dashboard.html`) présente un résumé visuel des métriques clés sans jargon technique. Les termes médicaux (IMC, taux de cholestérol, ratio macronutriments) sont accompagnés d'une explication en langage courant ou d'une infobulle accessible (`role="tooltip"`, navigable au clavier).

**Feedback immédiat et réassurance.** L'upload d'une photo de repas (`docs/maquettes/02-nutrition-upload.html`) affiche une prévisualisation locale avant envoi, puis un indicateur de progression et enfin le résultat ou le message de fallback. L'utilisateur n'est jamais laissé sans retour sur l'état de son action.

**Transparence sur l'IA.** Les résultats issus du service IA affichent le niveau de confiance (`confidence`) et signalent clairement les estimations fallback. Cette transparence évite la sur-confiance dans des valeurs génériques.

### Utilisateur malvoyant ou utilisant un lecteur d'écran

La navigation complète au clavier (Tab, Shift+Tab, Entrée, Espace, touches fléchées dans les listes) est garantie sur l'ensemble des pages. L'ordre de lecture du DOM correspond à l'ordre visuel de la page sur les trois breakpoints (mobile 375 px, tablette 768 px, desktop 1280 px).

Les images uploadées par l'utilisateur disposent d'un champ `alt` dynamique renseigné avec le nom du fichier ou "Image de repas analysée". Les graphiques de métriques (dashboard) sont accompagnés d'une table de données alternative masquée visuellement mais accessible (`class="sr-only"`).

Les annonces `aria-live` sont calibrées pour éviter la verbosité excessive : les mises à jour fréquentes (indicateurs de progression) utilisent `aria-live="polite"` pour ne pas interrompre la lecture en cours, tandis que les erreurs et changements d'état critiques utilisent `aria-live="assertive"` / `role="alert"`.

### Utilisateur mobile

Le design responsive en trois breakpoints (375 px / 768 px / 1280 px), défini dans `docs/maquettes/_shared.css` et appliqué aux sept wireframes, garantit une expérience utilisable sur smartphone sans zoom horizontal ni perte de contenu.

Les zones de touch sont dimensionnées à 44×44 px minimum (recommandation WCAG 2.5.5), ce qui inclut les boutons d'upload, les boutons de validation de formulaire et les liens de navigation. Les formulaires (`docs/maquettes/05-fitness-formulaire.html`) utilisent les types d'input sémantiques (`type="number"`, `type="email"`) pour déclencher le clavier virtuel adapté sur iOS et Android.

Le fallback de l'analyse IA est particulièrement important en contexte mobile, où la connectivité peut être intermittente. L'interface affiche immédiatement un résultat — estimé si nécessaire — plutôt que d'afficher un écran d'erreur bloquant, favorisant ainsi la continuité d'usage.
