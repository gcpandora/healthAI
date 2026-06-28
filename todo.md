# TODO — MSPR TPRE601 — HealthAI Coach

> Source de vérité du projet. Toute session Claude (Claude.ai, Claude Code en VS Code, etc.)
> qui reprend ce repo doit lire ce fichier en premier pour savoir où on en est.
> Mets-le à jour à chaque session de travail et commite-le avec le code.

**Dernière mise à jour :** 2026-06-28
**Repo :** https://github.com/tom-dab/healthAI · branche de travail principale : `develop`

---

## 🧭 Contexte

- **Projet :** HealthAI Coach — extension mini réseau social (app mobile + API publications + infra + monitoring)
- **Blocs évalués :** E6.3 (produire/maintenir solution IA) & E6.4 (gérer activités/tâches)
- **Équipe :**
  - Tom — DevOps / Chef de projet → CI/CD, Docker multi-env, monitoring, coordination
  - Hélie — Mobile → React Native/Expo, UI mini-réseau social
  - Tojo — Backend → API publications, endpoints médias, MinIO
  - Hanane — DBA → schéma publications/médias, migrations, sauvegarde/restauration
  - Houssem — ML/Data → qualité code, tests, documentation technique
- **TPRE501 + TPRE502 validées** — stack existante sur `develop` réutilisable telle quelle, ne pas réécrire l'API `:8000`.
- **Règle d'or :** tout tourne en Docker Compose, jamais d'install locale hors conteneur.

---

## 📍 État constaté du repo (vérifié par analyse directe, pas par déclaration)

| Élément | État |
|---|---|
| `develop` | Stack TPRE501/502 only — rien de TPRE601 |
| Branche `BD&stockage` | ✅ `V3__social_network.sql` (posts, media, comments, likes) + ERD-V3.png — **PAS ENCORE MERGÉE dans develop** |
| `docker-compose.yml` (develop) | Pas de `publications-api`, `minio`, `prometheus`, `grafana` |
| Mobile | Aucun projet Expo créé |
| CI (`.github/workflows/ci.yml`) | lint ruff → test-api → test-etl → build docker. Pas de SonarQube, pas de push image, pas de job deploy |
| Tags Git | Aucun |
| ⚠️ À nettoyer | `services/api/main.py` : mot de passe admin `"admin123"` en dur → variabiliser avant rendu |

---

## 🔥 P1 — Éliminatoires (28/28 restantes) — ordre d'attaque

### Phase 0 — Socle infra Docker (bloquant, à faire en premier) — Tom
- [ ] Maj `docker-compose.yml` : ajouter `publications-api:8003`, `minio:9000`, `prometheus:9090`, `grafana:3003`
- [ ] Configuration MinIO (bucket `healthai-media`, policy public-read)
- [ ] Dockerfiles nouveaux services (`publications-api` Python slim, multi-stage si besoin)

### Phase 1 — Backend Publications — Hanane / Tojo
- [x] Schéma PostgreSQL publications — **fait sur branche `BD&stockage`, à merger dans `develop`**
- [x] Migration `V3__social_network.sql` — **idem, à merger**
- [x] Structure service FastAPI publications `:8004` (routes CRUD `/posts`, `/posts/{id}`, pagination cursor-based) — **`feature/publications-api-v1` le 2026-06-28**
- [ ] Endpoint upload média (`POST /media/upload` → MinIO, URL signée, validation type/taille)
- [x] Auth JWT partagée (réutiliser secret HS256 de l'API `:8000`, middleware commun) — **`feature/publications-api-v1` le 2026-06-28**

> ⏩ **Action immédiate suggérée :** merger `BD&stockage` → `develop` avant de commencer le service FastAPI, pour ne pas développer sur un schéma qui n'existe pas encore côté `develop`.

### Phase 2 — App mobile (livrable central, zéro existant) — Hélie
- [ ] Initialisation projet Expo (`create-expo-app`, TypeScript, structure dossiers)
- [ ] Navigation (Expo Router / React Navigation : tabs Flux/Créer/Profil + stack auth)
- [ ] Authentification JWT (Login/Register, appel API `:8000`, SecureStore)
- [ ] Flux de publications (feed infini : photo profil, nom, texte, média, likes, commentaires)
- [ ] Création de publication (texte + image/vidéo via `expo-image-picker`, upload, preview)
- [ ] Panneau de contrôle utilisateur (nom d'affichage, photo de profil MinIO, déconnexion)

> Peut démarrer **en parallèle de la Phase 1** avec une API mockée, à condition de stabiliser le contrat d'API (OpenAPI) en premier.

### Phase 3 — Multi-environnement Docker — Tom
- [ ] Profil `full` (toutes APIs IA réelles)
- [ ] Profil `offline` (mocks wiremock, données statiques seed)
- [ ] Profil `perf` (ressources réduites, monitoring simplifié)
- [ ] `start.sh` (`./start.sh [full|offline|perf]`, vérifie Docker, copie `.env`, < 10 min)
- [ ] Validation démarrage chronométré < 10 min sur machine froide

### Phase 4 — CI/CD — Tom / Houssem
- [ ] Workflow build+tests API existante (base déjà présente dans `ci.yml`, à enrichir : rapport coverage)
- [ ] Workflow build+tests API publications (badge couverture README)
- [ ] Workflow lint + qualité SonarQube (`sonar-scanner`, quality gate bloquant si couverture < 80%)

### Phase 5 — Monitoring — Tom
- [ ] Configuration Prometheus (scrape `api:8000`, `publications-api:8003`, node-exporter, cAdvisor)
- [ ] Dashboard Grafana — stack complète (CPU/RAM par container, req/s, taux erreur, latence p95)

### Phase 6 — Gestion de projet — Tom
- [ ] Tableau Kanban/Scrum opérationnel (Trello/Jira : Backlog/Sprint/En cours/Review/Done)

### Phase 7 — Soutenance (dépend de tout le reste) — Tom / Hélie
- [ ] Support de présentation orale (20 min : contexte, archi, démo, CI/CD, monitoring, gestion projet, difficultés, perspectives)
- [ ] Démo live fonctionnelle (`start.sh offline` → app mobile → post → Grafana en direct)
- [ ] Dépôt GitHub propre et complet (README à jour, tags de version, aucun secret en dur, CI verte)

---

## 📋 Backlog P2 / P3 (à traiter après les P1, par catégorie)

<details>
<summary>Application mobile — P2 (4)</summary>

- [ ] Likes et commentaires (POST like/unlike, chargement/ajout commentaires)
- [ ] Mode hors ligne / dégradé (cache local, indicateur de connexion)
- [ ] Build Android APK / iOS (EAS Build, profils dev/preview/production)
- [ ] Tests end-to-end mobile (Detox ou manuel)
</details>

<details>
<summary>API Publications — P2 (5)</summary>

- [ ] Endpoints likes et commentaires
- [ ] Endpoint profil utilisateur (`GET/PATCH /users/me/profile`)
- [ ] Exposition métriques Prometheus (`prometheus_fastapi_instrumentator`)
- [ ] Tests pytest API publications (couverture > 80%)
- [ ] Documentation OpenAPI (schémas Pydantic v2, exemples, swagger UI)
</details>

<details>
<summary>BDD & stockage — P2 (4) / P3 (1)</summary>

- [ ] Jeu de données démo (10 users, 30 posts, 20 médias, likes/commentaires)
- [ ] Script sauvegarde PostgreSQL (`backup.sh`, rotation 7 jours)
- [ ] Script restauration PostgreSQL (`restore.sh` + validation intégrité)
- [ ] Sauvegarde MinIO (mc mirror/snapshot)
- [ ] P3 — Index et performances (index `posts.user_id`, `posts.created_at`, contrainte unique `likes`)
</details>

<details>
<summary>Infrastructure Docker — P2 (3)</summary>

- [ ] Script de nettoyage `reset.sh`
- [ ] Health checks et `depends_on` sur tous les nouveaux services
- [ ] Documentation images conteneurs (base, ports, env, volumes)
</details>

<details>
<summary>CI/CD — P2 (5)</summary>

- [ ] Workflow build image Docker + push (GHCR/Docker Hub, tags `:latest` + `:sha`)
- [ ] Workflow déploiement automatique (job deploy conditionnel branche `main`)
- [ ] Gestion des secrets GitHub Actions (`SONAR_TOKEN`, `DOCKER_TOKEN`)
- [ ] Documentation pipeline CI/CD
- [ ] Rapport de tests automatisés (export JUnit XML, publication PR)
</details>

<details>
<summary>Monitoring — P2 (5)</summary>

- [ ] Dashboard Grafana — métriques applicatives (posts/min, uploads, users actifs)
- [ ] Alertes Grafana basiques (API down > 1min, RAM > 90%, erreurs > 5%)
- [ ] Logs centralisés (Loki + promtail)
- [ ] node-exporter + cAdvisor
- [ ] Documentation système de supervision
</details>

<details>
<summary>Tests & qualité — P2 (4) / P3 (1)</summary>

- [ ] Plan de test global
- [ ] Indicateurs qualité SonarQube (code smells, duplication, couverture, dette technique)
- [ ] Tests d'intégration API publications (scénario auth→post→upload→like→commentaire)
- [ ] Rapport de tests final
- [ ] P3 — Tests de charge (Locust/k6, 50 users simultanés)
</details>

<details>
<summary>Documentation & architecture — P2 (5)</summary>

- [ ] Diagramme architecture système global (UML/C4)
- [ ] Schéma déploiement Docker Compose
- [ ] Schéma BDD ERD (dbdiagram.io, V1+V2+V3)
- [ ] README principal mis à jour
- [ ] Variables d'environnement documentées (`.env.example` complet)
</details>

<details>
<summary>Gestion de projet agile — P2 (6)</summary>

- [ ] Sprint 1 — planification + rapport
- [ ] Sprint 2 — planification + rapport (+ rétro sprint 1)
- [ ] Sprint 3 — planification + rapport (stabilisation finale)
- [ ] Documentation des daily meetings (5-6 daily)
- [ ] Revues de sprint (démo interne)
- [ ] Rétrospectives de sprint (1 par sprint min.)
</details>

<details>
<summary>Bonus — P3 (1)</summary>

- [ ] Kubernetes mono-nœud (minikube) — manifests, helm chart optionnel
</details>

---

## 🧩 Mode d'emploi de ce fichier

1. Avant de commencer une tâche : vérifie son statut ici (pas seulement en mémoire/déclaration — un `git log`/`git branch -a` vaut mieux qu'un souvenir).
2. Une tâche = une branche `feature/<nom-tache>` depuis `develop`.
3. Une fois une tâche terminée et mergée : cocher la case ici, dans le même commit ou le suivant.
4. L'orchestration (choix de l'ordre, rédaction des prompts d'implémentation) se fait côté Claude.ai ; l'implémentation se fait côté Claude Code (VS Code) en collant le prompt fourni.
