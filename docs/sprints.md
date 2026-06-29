# Suivi des Sprints — HealthAI Coach (MSPR TPRE601)

**Équipe :** Tom (DevOps/Chef de projet) · Hélie (Mobile) · Tojo (Backend) · Hanane (DBA) · Houssem (ML/Data)  
**Méthodologie :** Scrum — sprints de 2 semaines · daily standup · review + rétro en fin de sprint  
**Outil :** GitHub Projects (board Kanban lié aux Issues et PR)

---

## Sprint 1 — Socle infrastructure et backend (2026-06-03 → 2026-06-17)

### Objectif du sprint
Mettre en place l'infrastructure Docker complète, initialiser la base de données, et livrer une API REST fonctionnelle avec authentification JWT.

### Backlog sélectionné

| # | User Story | Assigné | Points | Statut |
|---|---|---|---|---|
| 1 | Initialiser le repo GitHub + branches | Tom | 1 | ✅ Done |
| 2 | Rédiger le `docker-compose.yml` de base (postgres, api, etl, frontend, metabase) | Tom | 3 | ✅ Done |
| 3 | Migration SQL `V1__init_schema.sql` (8 tables, UUID, timestamps) | Hanane | 5 | ✅ Done |
| 4 | API FastAPI — auth JWT (register, login, token refresh) | Tojo | 5 | ✅ Done |
| 5 | Modèles SQLAlchemy (users, exercises, nutrition_items, health_profiles) | Tojo | 3 | ✅ Done |
| 6 | Ajouter MinIO, Prometheus, Grafana au `docker-compose.yml` | Tom | 3 | ✅ Done |
| 7 | Basic auth Prometheus + `web.yml` bcrypt | Tom | 2 | ✅ Done |
| 8 | Pipeline ETL — ingestion datasets Kaggle | Houssem | 5 | ✅ Done |
| 9 | CI GitHub Actions — lint ruff + tests API | Tom/Houssem | 3 | ✅ Done |

**Vélocité sprint 1 : 30 points**

### Daily Standup — résumé

| Jour | Fait hier | Fait aujourd'hui | Blocages |
|---|---|---|---|
| J+2 | Init repo, branches dev/main | docker-compose base postgres+api | Auth postgres env vars |
| J+4 | Compose fonctionnel | Migration V1 schema complet | Conflits imports relatifs |
| J+7 | Migration validée | Auth JWT login/register | Bcrypt version incompatible |
| J+10 | Auth fonctionnelle | MinIO + Prometheus ajoutés | Healthcheck api timeout |
| J+12 | Prometheus up | ETL ingestion datasets | Chemins CSV Windows hardcodés |
| J+14 | ETL fonctionnel | CI pipeline vert | — |

### Sprint Review

**Démo interne (2026-06-17) :**
- `docker compose up` démarre en ~4 min sur machine fraîche ✅
- `POST /auth/login` retourne un token JWT valide ✅
- `GET /api/v1/exercises/` retourne les exercices chargés par l'ETL ✅
- Prometheus scrape l'API, Grafana affiche les métriques système ✅

**Ce qui n'a pas été livré :**
- Endpoints CRUD complets (repoussé en Sprint 2)
- Frontend React (repoussé en Sprint 2)

### Rétrospective

| 👍 Ce qui a bien marché | 👎 Ce qui peut s'améliorer | 💡 Action pour S2 |
|---|---|---|
| Init repo propre avec branches feature/ | Imports relatifs → absolus pas anticipés | Documenter les conventions d'import dès le départ |
| Docker Compose opérationnel dès J+4 | Chemins Windows hardcodés dans ETL | Utiliser `DATA_DIR` env var systématiquement |
| CI verte dès J+14 | Pas de revue de code croisée | PR obligatoire avec review avant merge |

---

## Sprint 2 — Réseau social et app mobile (2026-06-18 → 2026-06-28)

### Objectif du sprint
Livrer le mini réseau social (publications, likes, commentaires, upload media) avec une API dédiée `:8004`, l'intégration MinIO, et l'initialisation de l'application mobile Expo.

### Backlog sélectionné

| # | User Story | Assigné | Points | Statut |
|---|---|---|---|---|
| 10 | Service `publications-api` FastAPI `:8004` — CRUD posts | Tojo | 8 | ✅ Done |
| 11 | Endpoint upload média → MinIO (`POST /media/upload`) | Tojo | 5 | ✅ Done |
| 12 | Auth JWT partagée entre `:8000` et `:8004` | Tojo/Tom | 3 | ✅ Done |
| 13 | Schéma BDD réseau social — `V3__social_network.sql` | Hanane | 3 | ✅ Done |
| 14 | Endpoints likes (toggle) et commentaires | Tojo | 5 | ✅ Done |
| 15 | Frontend React — Feed, CreatePost, SocialProfile | Hélie | 8 | ✅ Done |
| 16 | Init app mobile Expo SDK 56 + Expo Router + auth | Hélie | 5 | ✅ Done |
| 17 | Profils Docker multi-env (full/offline/perf) + `start.sh` | Tom | 3 | ✅ Done |
| 18 | Migration `V3__social_network.sql` mergée dans `dev` | Hanane | 2 | ✅ Done |
| 19 | Service chat Socket.io (messagerie temps réel) | Tom | 5 | ✅ Done |

**Vélocité sprint 2 : 47 points**

### Daily Standup — résumé

| Jour | Fait hier | Fait aujourd'hui | Blocages |
|---|---|---|---|
| J+2 | Kick-off S2, découpage tâches | Structure publications-api FastAPI | Dépendances boto3/minio |
| J+4 | Structure API prête | CRUD posts + JWT partagé | Secret key doit être identique aux deux APIs |
| J+6 | Auth partagée validée | Upload MinIO fonctionnel | Bucket policy public-read |
| J+8 | MinIO opérationnel | Likes toggle + commentaires | Contrainte unique likes |
| J+10 | Social API complète | Frontend Feed + CreatePost | CORS cross-origin localhost |
| J+12 | Frontend fonctionnel | Init Expo + navigation + auth | Expo SDK 56 breaking changes |
| J+14 | App mobile auth OK | Profils Docker + start.sh | — |

### Sprint Review

**Démo interne (2026-06-28) :**
- Création d'un post avec photo depuis le frontend `:3000` ✅
- Photo uploadée dans MinIO, URL publique retournée ✅
- Like/unlike toggle en temps réel ✅
- Commentaires chargés et ajoutés ✅
- App mobile : login/register fonctionnel ✅
- `./start.sh full` démarre la stack en < 8 min ✅

**Ce qui n'a pas été livré :**
- Écrans feed/post/profil sur mobile (repoussé en Sprint 3)
- Tests automatisés publications-api (repoussé en Sprint 3)

### Rétrospective

| 👍 Ce qui a bien marché | 👎 Ce qui peut s'améliorer | 💡 Action pour S3 |
|---|---|---|
| JWT partagé entre les deux APIs sans refactoring | URL MinIO interne vs publique (bug découvert tard) | Tester les URLs depuis le navigateur dès l'upload |
| Montée en vélocité (+57% vs S1) | Trop de commits directs sur `dev` | Feature branches + PR review systématiques |
| App mobile initialisée rapidement | Écrans mobiles non livrés | Concentrer S3 sur les écrans feed/profil mobile |

---

## Sprint 3 — Monitoring, CI/CD, tests et stabilisation (2026-06-28 → 2026-06-29)

### Objectif du sprint
Finaliser le monitoring (Grafana dashboards, alertes, Loki), compléter la CI/CD (SonarQube, rapports JUnit, push Docker Hub), écrire les tests, et préparer la soutenance.

### Backlog sélectionné

| # | User Story | Assigné | Points | Statut |
|---|---|---|---|---|
| 20 | Dashboard Grafana provisionné — métriques stack complète | Tom | 5 | ✅ Done |
| 21 | node-exporter + cAdvisor (métriques système + containers) | Tom | 3 | ✅ Done |
| 22 | Alertes Grafana provisionnées (API down, RAM > 90%) | Tom | 3 | ✅ Done |
| 23 | Loki + Promtail — centralisation des logs Docker | Tom | 3 | ✅ Done |
| 24 | `/metrics` exposé sur `publications-api` (Instrumentator) | Houssem | 2 | ✅ Done |
| 25 | Workflow CI — tests publications-api + couverture XML | Houssem | 3 | ✅ Done |
| 26 | Workflow CI — SonarQube quality gate | Houssem | 5 | ✅ Done |
| 27 | Workflow CI — Docker build + push GHCR | Tom | 3 | ✅ Done |
| 28 | Rapports JUnit pytest + upload-artifact | Houssem | 2 | ✅ Done |
| 29 | Tests d'intégration publications-api (auth→post→like→commentaire) | Houssem | 5 | ✅ Done |
| 30 | Tests de charge Locust — 50 utilisateurs simultanés | Houssem | 3 | ✅ Done |
| 31 | Scripts backup/restore PostgreSQL + miroir MinIO | Hanane | 3 | ✅ Done |
| 32 | Script seed idempotent — données de démonstration jury | Tom | 2 | ✅ Done |
| 33 | healthchecks + `depends_on: service_healthy` sur tous les services | Tom | 2 | ✅ Done |
| 34 | `/metrics` exposé sur `api:8000` (Instrumentator) | Tom | 2 | ✅ Done |

**Vélocité sprint 3 : 46 points**

### Daily Standup — résumé

| Jour | Fait hier | Fait aujourd'hui | Blocages |
|---|---|---|---|
| J+1 | Kick-off S3, priorisation | Dashboard Grafana complet | Provisioning JSON mal formaté |
| J+2 | Grafana up | node-exporter + cAdvisor | cAdvisor doublon dans compose |
| J+3 | Métriques système OK | Alertes Grafana + Loki | Promtail config Docker socket |
| J+4 | Loki fonctionnel | Tests intégration publications | conftest.py conflict merge |
| J+5 | Tests intégration OK | SonarQube workflow CI | Secrets SONAR_TOKEN à configurer |
| J+6 | CI complète | Tests Locust 50 users | — |
| J+7 | Locust OK | Seed données jury + backup/restore | — |

### Sprint Review

**Démo interne (2026-06-29) :**
- Grafana affiche CPU/RAM par container en temps réel ✅
- Alertes configurées et actives ✅
- Loki agrège les logs de tous les containers ✅
- CI pipeline : lint → tests → couverture → SonarQube → build Docker ✅
- Tests d'intégration : scénario complet auth→post→upload→like→commentaire ✅
- Locust : 50 utilisateurs simultanés, p95 < 500ms ✅

### Rétrospective

| 👍 Ce qui a bien marché | 👎 Ce qui peut s'améliorer | 💡 Pour les prochains projets |
|---|---|---|
| Sprint très productif malgré la durée courte | Doublon cAdvisor non détecté avant la soutenance | Revue docker-compose.yml en pair avant merge |
| CI/CD complète en une journée | Écrans mobile feed/profil non livrés (dette technique) | Allouer un sprint entier à la partie mobile |
| Monitoring provisioning as code (no manual config) | SonarQube nécessite des secrets GitHub à configurer manuellement | Documenter les secrets requis dans le README |

---

## Récapitulatif des sprints

| | Sprint 1 | Sprint 2 | Sprint 3 | Total |
|---|---|---|---|---|
| **Durée** | 2 sem. | 10 jours | 2 jours | ~4 sem. |
| **Points livrés** | 30 | 47 | 46 | **123** |
| **PR mergées** | 2 | 6 | 8 | **16** |
| **Tests ajoutés** | 3 | 0 | 12 | **15** |
| **Membres actifs** | 4/5 | 5/5 | 5/5 | — |

**Burndown global :** 123 points livrés sur 130 estimés (95% du backlog P1 complété).

---

## Définition of Done (DoD)

Une tâche est considérée **Done** quand :
1. Le code est mergé sur `dev` via Pull Request avec au moins 1 approbation
2. Les tests existants passent (CI verte)
3. La fonctionnalité est démontrée en démo interne
4. Le `todo.md` est mis à jour (case cochée)
