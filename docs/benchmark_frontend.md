# Benchmark Frontend — React 18/Vite vs Vue 3 vs Angular

**Projet :** HealthAI Coach — MSPR TPRE502  
**Date :** Mai 2026  
**Auteur :** Équipe développement frontend

---

## Contexte et critères d'évaluation

Dans le cadre du développement de l'interface utilisateur d'HealthAI Coach, trois frameworks frontend majeurs ont été évalués : **React 18 avec Vite**, **Vue 3** et **Angular**. L'évaluation porte sur six critères déterminants pour un projet de startup en environnement d'examen avec contraintes de temps et stack IA asynchrone.

---

## Tableau comparatif

| Critère | React 18 / Vite | Vue 3 | Angular |
|---|---|---|---|
| **Courbe d'apprentissage** | Modérée — JSX intuitif, hooks bien documentés | Faible — Options API accessible, Composition API progressive | Élevée — TypeScript obligatoire, CLI imposant, concepts DI/NgModule |
| **Écosystème** | Très large — npm, bibliothèques tierces nombreuses, forte communauté | Large — écosystème officiel cohérent mais plus restreint | Complet mais fermé — tout fourni par Angular, peu de flexibilité |
| **Bundle size (production)** | ~45 KB (React core) + Vite tree-shaking agressif | ~35 KB (Vue runtime) | ~150-200 KB (framework complet inclus) |
| **HMR (Hot Module Replacement)** | Excellent avec Vite — < 50 ms en développement | Excellent avec Vite ou Nuxt | Correct avec Angular CLI — plus lent (200-500 ms) |
| **Accessibilité (a11y)** | Bibliothèques matures : react-aria, Radix UI, support ARIA natif | Support ARIA natif, moins d'outillage spécialisé | Bonne intégration CDK a11y, mais verbosité accrue |
| **APIs IA asynchrones** | Excellente gestion async/await, Suspense, concurrent rendering | Bonne — composables async, mais moins de primitives concurrentes | Bonne — RxJS/Observables adapté aux flux, overhead conceptuel |
| **Adoption marché** | 1er (npm : ~25M téléchargements/semaine) | 3e (~5M/semaine) | 2e (~3M/semaine) |
| **TypeScript** | Optionnel mais supporté nativement | Optionnel — intégration progressive | Obligatoire — première classe |
| **Intégration Docker/Vite** | Native — `vite build` produit un dossier `dist` directement servi par nginx | Native avec Vite | Via `ng build` — configuration plus verbeuse |

---

## Analyse par critère

### Courbe d'apprentissage

React avec les hooks (`useState`, `useEffect`, `useCallback`) présente une courbe d'apprentissage initialement plus abrupte que Vue, mais le modèle mental reste cohérent sur l'ensemble du projet. L'équipe disposant d'une expérience préalable en JavaScript et Python, le modèle fonctionnel de React s'est avéré plus naturel que le système de réactivité de Vue ou l'injection de dépendances d'Angular.

### Performances et bundle

Vite comme bundler apporte un avantage décisif sur les deux autres configurations par défaut. Son moteur ESM natif réduit le temps de démarrage du dev server à moins d'une seconde et produit des bundles optimisés par tree-shaking sans configuration supplémentaire. Angular reste le plus lourd à l'initialisation, ce qui pénalise le Time To Interactive (TTI) sur mobile — critique pour une application de santé consultée en mobilité.

### Gestion des APIs IA asynchrones

L'endpoint `/api/v1/vision/analyze-meal` reçoit une image et déclenche un appel cascade (Ollama → HuggingFace → fallback statique) avec des temps de réponse variables (2 à 30 secondes). React Concurrent Rendering et le hook `useTransition` permettent de gérer nativement ces états suspendus sans bloquer l'interface, ce que Vue et Angular ne proposent pas avec la même granularité. Les skeleton loaders implémentés dans `FitnessRecommendations.jsx` et `NutritionAI.jsx` exploitent directement cette architecture.

### Accessibilité

React dispose de l'écosystème a11y le plus mature. Les composants des wireframes (voir `docs/maquettes/`) implémentent `aria-live`, `role="alert"`, `aria-busy` via des patterns documentés dans la communauté React. Les bibliothèques Radix UI et React Aria (WAI-ARIA 1.2) auraient pu être intégrées facilement si le projet l'avait nécessité.

### Adoption et pérennité

Avec 25 millions de téléchargements hebdomadaires sur npm et un soutien actif de Meta, React représente le choix le plus sûr en termes de recrutement futur, de maintenance et de durée de vie des dépendances. C'est également le framework le plus demandé dans les offres d'emploi en développement web en France en 2024-2025.

---

## Conclusion

**React 18 combiné à Vite était le choix optimal pour HealthAI Coach** pour trois raisons convergentes :

1. **Vitesse de développement** : HMR sous 50 ms, configuration minimale grâce à Vite, écosystème npm immédiatement exploitable.
2. **Adéquation avec la stack IA** : le modèle concurrent de React gère naturellement les appels asynchrones à durée imprévisible (vision IA avec fallback cascade), sans surcouche RxJS ni abstraction supplémentaire.
3. **Accessibilité et robustesse** : les patterns ARIA supportés par React permettent d'implémenter les états dégradés (fallback 429, service indisponible) de manière lisible par les technologies d'assistance, critère non-fonctionnel prioritaire pour une application de santé.

Vue 3 aurait constitué une alternative acceptable pour un projet plus simple, mais sa communauté a11y moins développée et son écosystème de composants asynchrones moins mature auraient introduit de la friction. Angular aurait représenté un surcoût de configuration incompatible avec les contraintes de temps du projet.
