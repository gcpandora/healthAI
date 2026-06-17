# Benchmark Frontend — React vs Vue vs Angular
## MSPR TPRE502 — HealthAI Coach

---

## 1. Contexte de l'évaluation

Le frontend HealthAI Coach est une SPA (Single Page Application) qui consomme deux APIs :
- L'API REST TPRE501 (CRUD — profils, nutrition, exercices)
- L'API IA TPRE502 (recommandations LLM, analyse photo)

Les critères d'évaluation sont pondérés selon les contraintes du projet :
accessibilité WCAG AA obligatoire, équipe de 4 développeurs, délai de 3 mois.

---

## 2. Critères d'évaluation

| Critère | Poids | Justification |
|---|---|---|
| Courbe d'apprentissage | 25% | Équipe avec niveaux variés |
| Écosystème / bibliothèques | 20% | Intégrations à prévoir |
| Performance (LCP, FID) | 20% | Application santé temps réel |
| Accessibilité WCAG AA | 15% | Exigence cahier des charges |
| Maintenabilité | 10% | Code durable pour l'examen |
| Taille du bundle | 10% | UX mobile |

---

## 3. Comparatif détaillé

### 3.1 Courbe d'apprentissage (25%)

| Framework | Score /10 | Commentaire |
|---|---|---|
| **React** | 8/10 | JSX familier, nombreux tutos, documentation abondante |
| **Vue 3** | 9/10 | Syntaxe proche HTML, Options API + Composition API |
| **Angular** | 5/10 | TypeScript obligatoire, concepts avancés (DI, modules, decorators) |

### 3.2 Écosystème / bibliothèques (20%)

| Framework | Score /10 | Bibliothèques disponibles |
|---|---|---|
| **React** | 9/10 | React Query, Zustand, Recharts, React Hook Form, shadcn/ui |
| **Vue 3** | 7/10 | Pinia, VueUse, Chart.js, Vee-Validate |
| **Angular** | 8/10 | NgRx, Angular Material, PrimeNG, Reactive Forms |

### 3.3 Performance — Core Web Vitals (20%)

Benchmarks mesurés sur une application CRUD + graphiques similaires (source : web.dev, 2024) :

| Framework | LCP moyen | FID moyen | Bundle size (gzip) |
|---|---|---|---|
| **React 18** | 1.2s | 45ms | 42 KB |
| **Vue 3** | 1.1s | 38ms | 34 KB |
| **Angular 17** | 1.8s | 62ms | 78 KB |

### 3.4 Accessibilité WCAG AA (15%)

| Framework | Score /10 | Commentaire |
|---|---|---|
| **React** | 8/10 | React Aria (Adobe), axe-react, attributs ARIA faciles |
| **Vue 3** | 7/10 | Support ARIA natif correct, moins de libs dédiées |
| **Angular** | 9/10 | CDK A11y (Angular Material), focus management intégré |

### 3.5 Maintenabilité (10%)

| Framework | Score /10 | Commentaire |
|---|---|---|
| **React** | 8/10 | Composants fonctionnels + hooks, architecture libre |
| **Vue 3** | 8/10 | Single File Components clairs, structure imposée |
| **Angular** | 7/10 | Architecture stricte mais verbeux |

### 3.6 Taille du bundle (10%)

| Framework | Score /10 | |
|---|---|---|
| **React** | 7/10 | 42 KB gzip (+ libs tierces) |
| **Vue 3** | 9/10 | 34 KB gzip — le plus léger |
| **Angular** | 5/10 | 78 KB gzip — overhead important |

---

## 4. Scores finaux pondérés

| Framework | Courbe (25%) | Éco (20%) | Perf (20%) | A11y (15%) | Main (10%) | Bundle (10%) | **Total** |
|---|---|---|---|---|---|---|---|
| **React** | 2.00 | 1.80 | 1.60 | 1.20 | 0.80 | 0.70 | **8.10/10** |
| **Vue 3** | 2.25 | 1.40 | 1.65 | 1.05 | 0.80 | 0.90 | **8.05/10** |
| **Angular** | 1.25 | 1.60 | 1.20 | 1.35 | 0.70 | 0.50 | **6.60/10** |

---

## 5. Décision : React 18 + Vite

**React est retenu** avec un score de 8.10/10.

### Justifications principales

1. **Adoption dans l'équipe** : React est le framework le mieux connu par les membres du groupe, réduisant le risque d'échec lié à l'apprentissage.

2. **React Query** : gestion du cache des appels API intégrée, idéale pour les appels vers l'API IA (qui peut être lente — jusqu'à 8s avec Ollama). React Query gère nativement le loading state, l'invalidation et le retry.

3. **Accessibilité** : React Aria (Adobe) est la bibliothèque d'accessibilité la plus complète du marché, garantissant la conformité WCAG AA requise.

4. **Vite** : le bundler choisi offre un HMR quasi-instantané en développement et des builds de production optimisés.

### Pourquoi pas Vue 3 ?
Vue 3 est très proche en score (8.05 vs 8.10). Le facteur décisif est la **taille de l'écosystème** : React dispose de plus de composants UI accessibles prêts à l'emploi (shadcn/ui, Radix UI) qui accélèrent le développement.

### Pourquoi pas Angular ?
Score significativement inférieur (6.60). La courbe d'apprentissage trop élevée et le bundle trop lourd ne sont pas justifiés pour ce projet.

---

## 6. Stack retenue

```
React 18 + Vite
├── React Query       — gestion des appels API + cache
├── React Router v6   — navigation SPA
├── Zustand           — état global léger
├── Recharts          — graphiques (activité, nutrition)
├── React Aria        — accessibilité WCAG AA
├── Tailwind CSS      — styles utilitaires
└── Axios             — client HTTP
```

---

## 7. Conformité WCAG AA — points critiques

| Critère WCAG | Implémentation React |
|---|---|
| 1.4.3 Contraste (AA) | Palette Tailwind vérifiée avec axe DevTools |
| 2.1.1 Clavier | React Aria — focus management automatique |
| 2.4.6 En-têtes descriptifs | Composants `<h1>...<h6>` sémantiques |
| 3.3.1 Identification des erreurs | Messages d'erreur associés aux champs (aria-describedby) |
| 4.1.2 Nom, rôle, valeur | Attributs ARIA sur tous les composants interactifs |
