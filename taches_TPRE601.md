# MSPR TPRE601 — HealthAI Coach
## Arborescence des tâches — Blocs E6.3 & E6.4 · EPSI Grenoble 2025-2026

> Source : `TPRE601_arborescence_taches.pdf`
> Équipe : **Tom** (DevOps/Chef de projet) · **Hélie** (Mobile) · **Tojo** (Backend) · **Hanane** (DBA) · **Houssem** (ML/Data/Tests)
> Légende : 🔴 **P1** — Éliminatoire · 🟡 **P2** — Important · 🟢 **P3** — Bonus / optionnel

---

## Résumé

| Bloc | Total | Fait | Restant | P1 ✅ | P2 ✅ | P3 ✅ |
|---|---|---|---|---|---|---|
| 1. Application mobile | 10 | 6 | 4 | 6/6 | 0/4 | — |
| 2. API Publications & médias | 8 | 7 | 1 | 3/3 | 4/5 | — |
| 3. Base de données & stockage | 8 | 7 | 1 | 3/3 | 4/4 | 0/1 |
| 4. Infrastructure Docker & multi-env | 10 | 9 | 1 | 7/7 | 2/3 | — |
| 5. CI/CD — GitHub Actions | 8 | 5 | 3 | 3/3 | 2/5 | — |
| 6. Monitoring & observabilité | 7 | 5 | 2 | 2/2 | 3/5 | — |
| 7. Tests & qualité de code | 5 | 2 | 3 | 0/0 | 1/4 | 1/1 |
| 8. Documentation & architecture | 5 | 0 | 5 | — | 0/5 | — |
| 9. Gestion de projet agile | 7 | 0 | 7 | 0/1 | 0/6 | — |
| 10. Soutenance & livrables finaux | 4 | 0 | 4 | 0/3 | — | 0/1 |
| **TOTAL** | **72** | **41** | **31** | **24/28** | **16/41** | **1/3** |

---

## 1. Application mobile (React Native / Expo) — 10 tâches

- [x] 🔴 **P1** — Initialisation projet Expo — *Hélie*
  `npx create-expo-app`, config TypeScript, structure dossiers (screens, components, hooks, api)
- [x] 🔴 **P1** — Navigation entre écrans — *Hélie*
  Expo Router ou React Navigation : tabs (Flux, Créer, Profil), stack auth (Login, Register)
- [x] 🔴 **P1** — Authentification JWT — *Hélie*
  Formulaires Login / Register, appel vers API :8000, stockage token SecureStore
- [x] 🔴 **P1** — Flux de publications (feed) — *Hélie*
  Liste infinie de posts avec photo de profil, nom d'affichage, texte, miniature média, likes et commentaires
- [x] 🔴 **P1** — Création de publication — *Hélie*
  Saisie texte, sélecteur image/vidéo (`expo-image-picker`), upload vers API, preview avant envoi
- [x] 🔴 **P1** — Panneau de contrôle utilisateur — *Hélie*
  Affichage et édition du nom d'affichage, photo de profil (upload MinIO), bouton déconnexion
- [ ] 🟡 **P2** — Likes et commentaires — *Hélie*
  Actions POST like/unlike, chargement des commentaires, ajout commentaire inline sur le flux
- [ ] 🟡 **P2** — Mode hors ligne / dégradé — *Hélie*
  Affichage données en cache si API indisponible, indicateur de connexion visible
- [ ] 🟡 **P2** — Build Android APK / iOS (EAS Build) — *Hélie*
  Config `eas.json`, profils dev/preview/production, génération APK démontrable pour le jury
- [ ] 🟡 **P2** — Tests end-to-end mobile — *Hélie, Houssem*
  Scénarios : login, post texte, post image, like, édition profil, déconnexion — Detox ou manuel

## 2. API Publications & médias (nouveau service) — 8 tâches

- [x] 🔴 **P1** — Structure service FastAPI publications — *Tojo*
  Nouveau container :8003, routes CRUD posts (`/posts`, `/posts/{id}`), pagination cursor-based
- [x] 🔴 **P1** — Endpoint upload média — *Tojo*
  `POST /media/upload` → stockage MinIO, retour URL signée, validation type et taille fichier
- [x] 🟡 **P2** — Endpoints likes et commentaires — *Tojo*
  `POST/DELETE /posts/{id}/like`, `GET/POST /posts/{id}/comments` avec pagination
- [x] 🟡 **P2** — Endpoint profil utilisateur — *Tojo*
  `GET/PATCH /users/me/profile` : display_name, avatar_url (MinIO), bio courte
- [x] 🔴 **P1** — Authentification JWT partagée — *Tojo*
  Réutiliser le secret HS256 de l'API :8000, middleware de validation commun entre services
- [x] 🟡 **P2** — Exposition métriques Prometheus — *Tojo*
  `prometheus_fastapi_instrumentator` sur `/metrics`, compteurs de requêtes et latence par endpoint
- [x] 🟡 **P2** — Tests pytest API publications — *Houssem*
  Couverture > 80% : CRUD posts, upload mock MinIO, vérification auth, pagination correcte
- [ ] 🟡 **P2** — Documentation OpenAPI — *Tojo*
  Descriptions des routes, schémas Pydantic v2, exemples de requêtes et réponses, swagger UI

## 3. Base de données & stockage — 8 tâches

- [x] 🔴 **P1** — Schéma PostgreSQL publications — *Hanane*
  Tables : posts (id UUID, user_id, content, media_urls[], created_at), likes, comments, user_profiles
- [x] 🔴 **P1** — Migration Flyway / Alembic V3 — *Hanane*
  Fichier migration versionné pour les nouvelles tables, compatible avec V1 et V2 existantes
- [x] 🔴 **P1** — Configuration MinIO (Docker) — *Hanane, Tom*
  Service minio :9000/:9001 (console), bucket `healthai-media`, policy public-read pour médias
- [x] 🟡 **P2** — Jeu de données de démonstration — *Hanane*
  Script seed : 10 utilisateurs, 30 posts, 20 médias, likes et commentaires — prêt pour le jury
- [x] 🟡 **P2** — Script de sauvegarde PostgreSQL — *Hanane*
  `backup.sh` : pg_dump schedulé, rotation 7 jours, stockage local dans `/backups` avec horodatage
- [x] 🟡 **P2** — Script de restauration PostgreSQL — *Hanane*
  `restore.sh` : pg_restore + validation intégrité des données, documentation des étapes
- [x] 🟡 **P2** — Sauvegarde MinIO (buckets) — *Hanane*
  `mc mirror` ou snapshot vers volume local, script de restauration avec vérification contenu
- [ ] 🟢 **P3** — Index et performances — *Hanane*
  Index sur `posts.user_id`, `posts.created_at`, contrainte unique `likes(post_id, user_id)`, EXPLAIN ANALYZE

## 4. Infrastructure Docker & multi-environnement — 10 tâches

- [x] 🔴 **P1** — Mise à jour `docker-compose.yml` base — *Tom*
  Ajout services : publications-api :8003, minio :9000, prometheus :9090, grafana :3003
- [x] 🔴 **P1** — Profil Docker Compose — full — *Tom*
  `docker-compose.full.yml` ou `--profile full` : tous les services actifs, APIs IA réelles fonctionnelles
- [x] 🔴 **P1** — Profil Docker Compose — offline — *Tom*
  `docker-compose.offline.yml` : mocks des APIs externes (wiremock), données statiques seed préchargées
- [x] 🔴 **P1** — Profil Docker Compose — perf — *Tom*
  `docker-compose.perf.yml` : réduction ressources (mem_limit), services allégés, monitoring simplifié
- [x] 🔴 **P1** — Script de démarrage unique (`start.sh`) — *Tom*
  Usage : `./start.sh [full|offline|perf]` — vérifie Docker, copie `.env`, lance le bon profil en < 10 min
- [x] 🟡 **P2** — Script de nettoyage (`reset.sh`) — *Tom*
  Stoppe les containers, supprime les volumes, recharge le seed — remise à zéro propre pour jury
- [x] 🔴 **P1** — Dockerfiles nouveaux services — *Tom, Tojo*
  Dockerfile publications-api (Python slim), multi-stage build si nécessaire, `.dockerignore` complet
- [x] 🟡 **P2** — Health checks et `depends_on` — *Tom*
  Conditions healthcheck sur postgres, minio, api avant démarrage des services dépendants
- [ ] 🟡 **P2** — Documentation images conteneurs — *Tom*
  Pour chaque image : base utilisée, ports, variables d'env, volumes montés, commandes utiles
- [x] 🔴 **P1** — Validation démarrage < 10 minutes — *Tom*
  Test chronométré sur machine froide, optimisation pull et cache des images si dépassement

## 5. CI/CD — GitHub Actions — 8 tâches

- [x] 🔴 **P1** — Workflow build + tests API existante — *Tom*
  `.github/workflows/api.yml` : checkout, pip install, pytest, génération rapport coverage
- [x] 🔴 **P1** — Workflow build + tests API publications — *Tom*
  Idem pour le nouveau service :8003, badge de couverture affiché dans le README
- [x] 🔴 **P1** — Workflow lint et qualité (SonarQube) — *Tom, Houssem*
  sonar-scanner, `sonar-project.properties`, quality gate bloquant si couverture < 80%
- [x] 🟡 **P2** — Workflow build image Docker et push — *Tom*
  `docker/build-push-action` vers GHCR ou Docker Hub, tags `:latest` + `:sha` de commit
- [ ] 🟡 **P2** — Workflow déploiement automatique — *Tom*
  Job deploy conditionnel (branche main uniquement), ssh/docker-compose pull+up en remote
- [ ] 🟡 **P2** — Gestion des secrets GitHub Actions — *Tom*
  Secrets repo : SONAR_TOKEN, DOCKER_TOKEN — aucun secret hardcodé dans le code
- [ ] 🟡 **P2** — Documentation pipeline CI/CD — *Tom*
  Schéma du pipeline, description de chaque job, comment modifier ou ajouter des étapes
- [x] 🟡 **P2** — Rapport de tests automatisés — *Houssem*
  Export JUnit XML depuis pytest, publication dans les PR et comme artefact GitHub Actions

## 6. Monitoring & observabilité — 7 tâches

- [x] 🔴 **P1** — Configuration Prometheus — *Tom*
  `prometheus.yml` : scrape configs pour api :8000, publications-api :8003, node-exporter, cadvisor
- [x] 🔴 **P1** — Dashboard Grafana — stack complète — *Tom*
  Dashboard JSON provisionné : CPU/RAM par container, req/s par API, taux d'erreur, latence p95
- [ ] 🟡 **P2** — Dashboard Grafana — métriques applicatives — *Tom*
  Posts créés/min, uploads média réussis, utilisateurs actifs, hits/miss cache applicatif
- [x] 🟡 **P2** — Alertes Grafana basiques — *Tom*
  Alerte si API down > 1 min, RAM > 90%, taux d'erreur HTTP > 5% — démonstrable au jury
- [x] 🟡 **P2** — Logs centralisés (Loki + promtail) — *Tom*
  Collecte logs containers Docker, visualisation dans Grafana, recherche par service et niveau
- [x] 🟡 **P2** — node-exporter + cAdvisor — *Tom*
  Services Docker pour métriques système hôte et métriques containers, scraping Prometheus
- [ ] 🟡 **P2** — Documentation système de supervision — *Tom, Houssem*
  Liste exhaustive des métriques collectées, procédure accès dashboards, lecture des alertes

## 7. Tests & qualité de code — 5 tâches

- [ ] 🟡 **P2** — Plan de test global — *Houssem*
  Document : périmètre, types de tests (unit, intégration, e2e, charge), critères d'acceptation
- [ ] 🟡 **P2** — Indicateurs qualité SonarQube — *Houssem*
  Rapport : code smells, duplications, couverture, dette technique — valeurs cibles définies et atteintes
- [x] 🟡 **P2** — Tests d'intégration API publications — *Houssem*
  Scénarios complets : auth → post → upload → like → commentaire, avec base de données réelle
- [x] 🟢 **P3** — Tests de charge basiques (Locust / k6) — *Houssem*
  Scénario 50 utilisateurs simultanés, rapport temps de réponse, identification des goulots
- [ ] 🟡 **P2** — Rapport de tests final — *Houssem*
  Synthèse : taux de réussite, bugs détectés et corrigés, indicateurs qualité finaux à date livraison

## 8. Documentation & architecture — 5 tâches

- [ ] 🟡 **P2** — Diagramme architecture système global — *Tom*
  UML composants ou C4 : tous les services, flux de données, ports exposés, dépendances inter-services
- [ ] 🟡 **P2** — Schéma déploiement Docker Compose — *Tom*
  Schéma visuel : containers, réseaux Docker internes, volumes montés, profils d'environnement
- [ ] 🟡 **P2** — Schéma BDD (ERD) — *Hanane*
  Toutes les tables PostgreSQL (V1+V2+V3), relations, clés étrangères — outil dbdiagram.io
- [ ] 🟡 **P2** — README principal mis à jour — *Tom*
  Installation pas-à-pas, prérequis, variables `.env`, commandes de démarrage, liens vers docs
- [ ] 🟡 **P2** — Variables d'environnement documentées — *Tom*
  `.env.example` complet commenté, documentation de chaque variable avec valeurs acceptées et défaut

## 9. Gestion de projet agile — 7 tâches

- [ ] 🔴 **P1** — Tableau Kanban/Scrum opérationnel — *Tom*
  Trello ou Jira : colonnes Backlog/Sprint/En cours/Review/Done, toutes les tâches créées et assignées
- [ ] 🟡 **P2** — Sprint 1 — planification + rapport — *Tom*
  Objectifs sprint, user stories, points attribués (story points), rapport réalisations vs objectifs
- [ ] 🟡 **P2** — Sprint 2 — planification + rapport — *Tom*
  Idem sprint 1, incluant rétrospective sprint 1 et ajustements de vélocité de l'équipe
- [ ] 🟡 **P2** — Sprint 3 — planification + rapport — *Tom*
  Dernier sprint, focus stabilisation et documentation, rapport final d'avancement global
- [ ] 🟡 **P2** — Documentation des daily meetings — *Tom*
  Compte-rendu synthétique de 5 à 6 daily : qui a fait quoi, blocages rencontrés, actions planifiées
- [ ] 🟡 **P2** — Revues de sprint (démo interne) — *Tom*
  Présentation des fonctionnalités livrées à chaque fin de sprint, feedback de l'équipe consigné
- [ ] 🟡 **P2** — Rétrospectives de sprint — *Tom*
  Ce qui a bien marché / à améliorer / actions concrètes décidées — minimum 1 par sprint

## 10. Soutenance & livrables finaux — 4 tâches

- [ ] 🔴 **P1** — Support de présentation orale (20 min) — *Tom*
  Slides : contexte, architecture, démo, CI/CD, monitoring, gestion projet, difficultés rencontrées, perspectives
- [ ] 🔴 **P1** — Démo live fonctionnelle pour jury — *Tom, Hélie*
  Scénario démontrable : `start.sh offline` → app mobile → création post → monitoring Grafana en direct
- [ ] 🔴 **P1** — Dépôt GitHub propre et complet — *Tom*
  README à jour, structure claire, tags de version, aucun secret dans le code, pipeline CI verte
- [ ] 🟢 **P3** — Bonus — Kubernetes mono-nœud (minikube) — *Tom*
  Fichiers manifests K8s pour les services principaux, helm chart optionnel, documentation complète

---

*Cocher les cases au fur et à mesure de l'avancement. Fichier généré à partir de `TPRE601_arborescence_taches.pdf`.*
