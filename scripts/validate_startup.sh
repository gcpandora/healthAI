#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# validate_startup.sh — Lance la stack et vérifie que tout démarre en < 10 min
# Usage : ./scripts/validate_startup.sh [--profile full|offline|perf]
# Exit 0 = OK, Exit 1 = KO (timeout ou service non healthy)
# ─────────────────────────────────────────────────────────────────────────────

TIMEOUT_SECONDS=600   # 10 minutes
POLL_INTERVAL=5
COMPOSE_PROFILE="${1:-}"

START_TS=$(date +%s)
ERRORS=()

log()  { echo "[$(date +%H:%M:%S)] $*"; }
ok()   { echo "  ✔  $*"; }
fail() { echo "  ✘  $*"; ERRORS+=("$*"); }

elapsed() {
  local now
  now=$(date +%s)
  echo $(( now - START_TS ))
}

fmt_elapsed() {
  local s=$1
  printf "%dm%02ds" $(( s / 60 )) $(( s % 60 ))
}

# ── 1. Vérifications préalables ────────────────────────────────────────────
log "Vérification des prérequis..."

if ! command -v docker &>/dev/null; then
  echo "ERREUR : Docker n'est pas installé."
  exit 1
fi

if ! docker info &>/dev/null; then
  echo "ERREUR : Le démon Docker n'est pas démarré."
  exit 1
fi

if [[ ! -f ".env" ]]; then
  if [[ -f ".env.example" ]]; then
    log ".env manquant — copie depuis .env.example"
    cp .env.example .env
  else
    echo "ERREUR : .env introuvable et .env.example absent."
    exit 1
  fi
fi

# ── 2. Démarrage de la stack ───────────────────────────────────────────────
COMPOSE_ARGS=("up" "-d" "--build" "--remove-orphans")
if [[ -n "$COMPOSE_PROFILE" ]]; then
  COMPOSE_ARGS=("--profile" "$COMPOSE_PROFILE" "${COMPOSE_ARGS[@]}")
  log "Démarrage stack Docker (profil : $COMPOSE_PROFILE)..."
else
  log "Démarrage stack Docker (profil par défaut)..."
fi

docker compose "${COMPOSE_ARGS[@]}"
log "Containers lancés — attente que les healthchecks passent..."

# ── 3. Fonction : attendre qu'un container soit healthy ───────────────────
wait_healthy() {
  local name="$1"
  local deadline=$(( START_TS + TIMEOUT_SECONDS ))

  while true; do
    local status
    status=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$name" 2>/dev/null || echo "missing")

    case "$status" in
      healthy) return 0 ;;
      unhealthy)
        fail "Container $name est unhealthy"
        return 1
        ;;
      missing)
        fail "Container $name introuvable"
        return 1
        ;;
    esac

    if (( $(date +%s) >= deadline )); then
      fail "Timeout : $name n'est pas healthy après $(fmt_elapsed "$(elapsed)")"
      return 1
    fi

    sleep "$POLL_INTERVAL"
  done
}

# ── 4. Fonction : attendre qu'un endpoint HTTP réponde ────────────────────
wait_http() {
  local label="$1"
  local url="$2"
  local deadline=$(( START_TS + TIMEOUT_SECONDS ))

  while true; do
    if curl -sf --max-time 3 "$url" &>/dev/null; then
      return 0
    fi

    if (( $(date +%s) >= deadline )); then
      fail "Timeout : $label ($url) ne répond pas après $(fmt_elapsed "$(elapsed)")"
      return 1
    fi

    sleep "$POLL_INTERVAL"
  done
}

# ── 5. Vérification de chaque service ─────────────────────────────────────

# Services avec healthcheck Docker natif
HEALTHY_SERVICES=(
  "healthai_postgres"
  "healthai_minio"
)

# publications-api a un healthcheck mais on attend aussi qu'il soit up
if docker ps --format '{{.Names}}' | grep -q "healthai_publications_api"; then
  HEALTHY_SERVICES+=("healthai_publications_api")
fi

log "Attente des healthchecks natifs..."
for svc in "${HEALTHY_SERVICES[@]}"; do
  log "  → $svc..."
  if wait_healthy "$svc"; then
    ok "$svc healthy"
  fi
done

# Services sans healthcheck — on poll l'endpoint HTTP
log "Vérification des endpoints HTTP..."

declare -A HTTP_CHECKS=(
  ["API :8000"]="http://localhost:8000/health"
  ["Prometheus :9090"]="http://localhost:9090/-/healthy"
  ["Grafana :3003"]="http://localhost:3003/api/health"
)

# publications-api HTTP si présent
if docker ps --format '{{.Names}}' | grep -q "healthai_publications_api"; then
  HTTP_CHECKS["Publications-API :8004"]="http://localhost:8004/health"
fi

for label in "${!HTTP_CHECKS[@]}"; do
  url="${HTTP_CHECKS[$label]}"
  log "  → $label ($url)..."
  if wait_http "$label" "$url"; then
    ok "$label répond"
  fi
done

# ── 6. Résultat final ──────────────────────────────────────────────────────
ELAPSED=$(elapsed)
ELAPSED_FMT=$(fmt_elapsed "$ELAPSED")

echo ""
echo "════════════════════════════════════════════════════════"
if (( ${#ERRORS[@]} == 0 )); then
  echo "  RÉSULTAT : ✔  OK — Stack démarrée en ${ELAPSED_FMT}"
  echo "════════════════════════════════════════════════════════"
  exit 0
else
  echo "  RÉSULTAT : ✘  KO — ${#ERRORS[@]} erreur(s) en ${ELAPSED_FMT}"
  for e in "${ERRORS[@]}"; do
    echo "    • $e"
  done
  echo "════════════════════════════════════════════════════════"
  exit 1
fi
