# Maquettes HealthAI Coach — MSPR TPRE502

Wireframes interactifs basse-fidélité de l'application HealthAI Coach.
Chaque fichier HTML est autonome et s'ouvre directement dans un navigateur.
La feuille de styles partagée est `_shared.css` (référencée par `<link>`).

---

## Liste des écrans

| Fichier | Page | État représenté |
|---|---|---|
| [01-dashboard.html](01-dashboard.html) | Dashboard principal | Vue post-login : KPIs, tableaux, export CSV |
| [02-nutrition-upload.html](02-nutrition-upload.html) | Analyse nutritionnelle | État initial : dropzone vide, bouton désactivé |
| [03-nutrition-resultat.html](03-nutrition-resultat.html) | Analyse nutritionnelle | Résultat nominal : aliments, macros, balance, conseils |
| [04-nutrition-degrade.html](04-nutrition-degrade.html) | Analyse nutritionnelle | État dégradé : erreur API + fallback visible + quota 429 |
| [05-fitness-formulaire.html](05-fitness-formulaire.html) | Recommandations fitness | Formulaire profil complet + validation en erreur |
| [06-fitness-resultat.html](06-fitness-resultat.html) | Recommandations fitness | Programme IA généré : résumé, stats, séances, exercices |
| [07-fitness-skeleton.html](07-fitness-skeleton.html) | Recommandations fitness | Chargement : skeleton loader animé, formulaire verrouillé |

---

## Convention de lecture

Chaque fichier affiche **3 colonnes côte à côte**, chacune simulant un breakpoint :

- **Desktop ≥ 1024 px** — sidebar déployée (180 px) + contenu principal
- **Tablette 768 px** — sidebar réduite à icônes (50 px) + contenu adapté
- **Mobile 375 px** — pas de sidebar, header mobile avec hamburger, contenu empilé

Le style wireframe utilise une palette gris/blanc sans couleurs finales, sauf les badges
de statut (vert/orange/rouge) qui sont intentionnels car ils illustrent les indicateurs
d'état accessibles (différenciés par texte ET forme, pas seulement couleur).

---

## Choix UX — un paragraphe par écran

### WF-01 — Dashboard principal
Le dashboard adopte une grille de KPI à 5 colonnes sur desktop, réduite à 3+2 sur tablette
et 2+2 sur mobile, pour conserver la lisibilité des valeurs chiffrées sans scroll horizontal.
Les trois tableaux de détail (By Plan, By Gender, Quick Stats) passent de 3 colonnes à 2 puis
1 selon le breakpoint. Le bouton "Export CSV" est positionné en haut à droite en desktop (standard
admin), et descend sous les KPIs en mobile pour ne pas concurrencer l'information principale.
L'état système est toujours exprimé avec texte ET icône pour être perçu sans la couleur verte.

### WF-02 — Analyse nutritionnelle · Upload
La dropzone occupe toute la largeur de sa colonne avec un contraste de bordure en pointillés
(dashed) suffisant pour être identifiée comme zone interactive. Sur desktop, le panneau droit
affiche un empty state explicite (icône + texte) afin de signaler à l'utilisateur ce qui se
passera après soumission. Le bouton "Analyser" est intentionnellement désactivé tant qu'aucun
fichier n'est sélectionné — mais il reste focusable (aria-disabled vs disabled HTML) pour
que les lecteurs d'écran informent l'utilisateur de son existence et de sa condition. La section
"Récupérer une analyse passée" est placée en bas, hors du flux principal, et présentée en
accordéon sur mobile pour économiser l'espace.

### WF-03 — Analyse nutritionnelle · Résultat nominal
La ResultCard est construite selon une progression logique : aliments identifiés → calories →
macronutriments → balance → conseils → identifiant technique. Les barres de macronutriments
utilisent le composant `role="meter"` avec `aria-valuenow`, `aria-valuemin` et `aria-valuemax`
pour rendre les valeurs accessibles aux lecteurs d'écran. Le badge de balance nutritionnelle
("Équilibré ✓") combine icône, couleur et texte — trois canaux distincts de communication
d'état, conformément aux critères WCAG 1.4.1. Sur mobile, la photo aperçu est réduite mais
conservée pour le contexte visuel.

### WF-04 — Analyse nutritionnelle · État dégradé
Deux scénarios d'erreur sont représentés simultanément sur desktop pour illustrer la variété
des états : l'erreur de timeout (API lente) déclenche un fallback automatique avec résultat
partiel, tandis que le statut 429 (quota atteint) affiche un message d'attente. Le badge
"⚠ Mode dégradé" est positionné en regard du titre de la ResultCard avec `role="alert"` et
`aria-live="assertive"` pour une annonce immédiate aux technologies d'assistance. Les valeurs
approximatives sont préfixées "~" dans le texte (pas seulement visuellement) et les barres de
macros utilisent un fond jaune en complément de couleur pour le double codage. Sur mobile, le
header prend une teinte rouge foncée comme signal d'état global.

### WF-05 — Recommandations fitness · Formulaire profil
Le formulaire suit l'ordre d'importance : objectif (le plus structurant) → données biométriques
(âge, genre, poids, taille) → niveau → limitations → équipement. Les champs obligatoires sont
marqués visuellement par un astérisque et sémantiquement par `aria-required="true"`. L'état
d'erreur de validation est démontré sur la colonne tablette avec `aria-invalid="true"` et
`aria-describedby` pointant vers le message d'erreur, lequel porte `role="alert"`. Les chips
de limitations et d'équipement implémentent `role="checkbox"` + `aria-checked` + `tabindex="0"`
pour simuler des contrôles de formulaire accessibles sans input HTML caché. Sur mobile, les
champs poids et taille restent côte à côte (2 colonnes) car ils sont courts et conceptuellement
liés.

### WF-06 — Recommandations fitness · Résultat
Le résultat s'organise en trois niveaux d'information décroissants : résumé narratif (phrase
expliquant le programme et les adaptations à la limitation) → métriques quantitatives (séances,
calories, durée) → séances détaillées (exercices, séries, repos). Sur desktop, le formulaire
est compressé en lecture seule sur la gauche pour rappeler le profil utilisé sans occuper l'espace
dominant. Sur mobile, le profil est représenté par des chips compactes en haut de page. Les
notes spécifiques aux limitations (ex. "Flexion genou max 90°") sont visibles dans chaque
séance concernée, évitant à l'utilisateur de devoir faire le lien lui-même.

### WF-07 — Recommandations fitness · Skeleton loader
Le skeleton loader remplace exactement les zones qui seront occupées par le contenu réel :
une ligne large pour le titre, deux lignes pour le résumé, trois blocs carrés pour les stats
et trois cartes rectangulaires pour les séances. Cette correspondance géométrique entre squelette
et contenu évite le "layout shift" (CLS) lors du chargement. L'animation `shimmer` CSS simule
le mouvement de balayage lumineux. Le conteneur entier porte `aria-busy="true"` et un nœud
frère visible porte `role="status"` + `aria-live="polite"` avec un message texte, permettant
aux lecteurs d'écran d'annoncer l'état de chargement sans interrompre la navigation. Le formulaire
soumis est visuellement grisé et désactivé pour éviter une double soumission, tout en restant
affiché pour que l'utilisateur voit les données qu'il a fournies.

---

## Critères accessibilité transversaux

| Critère | Implémentation |
|---|---|
| **Focus clavier visible** | `outline: 3px solid #2563eb` sur tous les éléments interactifs |
| **Labels sur tous les champs** | `<label for="…">` systématique, `<fieldset>` + `<legend>` pour groupes |
| **États non-couleur** | Texte + icône + forme sur tous les badges et alertes |
| **Zones d'état dynamiques** | `aria-live="polite"` (quota, chargement) et `aria-live="assertive"` (erreurs) |
| **Navigation clavier dropzone** | `role="button"` + `tabindex="0"` + gestionnaire `keydown` Enter/Espace |
| **Landmarks HTML5** | `<nav>`, `<main>`, `<header>`, `<section>`, `<article>`, `<form>` |
| **Contraste minimum** | Texte sombre (#333) sur fond clair (#fff/#f8fafc) — ratio AA ≥ 4.5:1 |
| **Mobile : cible tactile** | Boutons et chips ≥ 40px de hauteur (WCAG 2.5.5) |

---

## Notes techniques

- Les animations CSS (`shimmer`, `pulse`) respectent le principe de `prefers-reduced-motion`
  — à ajouter en production via `@media (prefers-reduced-motion: reduce) { animation: none }`.
- Les wireframes n'intègrent pas les couleurs finales de la charte React (`#3498db` primary).
  La palette gris/blanc est intentionnelle pour rester au niveau wireframe.
- Les données affichées (noms d'aliments, valeurs, exercices) sont des exemples représentatifs
  des vraies réponses API de `visionAPI.analyze()` et `recommendationsAPI.getRecommendations()`.
