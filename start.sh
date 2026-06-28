#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-full}"
START_TS=$(date +%s)

# ── 1. Validation de l'argument ───────────────────────────────
case "$PROFILE" in
  full|offline|perf) ;;
  *)
    echo "Usage: ./start.sh [full|offline|perf]"
    echo "  full    — toutes les intégrations réelles (défaut)"
    echo "  offline — HuggingFace mocké, pas de connexion externe"
    echo "  perf    — ressources réduites, monitoring allégé"
    exit 1
    ;;
esac

# ── 2. Vérification Docker ────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "ERREUR : Docker n'est pas installé." >&2; exit 1
fi
if ! docker info &>/dev/null; then
  echo "ERREUR : Docker n'est pas démarré (ou droits insuffisants)." >&2; exit 1
fi

# ── 3. Vérification du fichier override ───────────────────────
OVERRIDE="docker-compose.${PROFILE}.yml"
if [ ! -f "$OVERRIDE" ]; then
  echo "ERREUR : fichier '$OVERRIDE' introuvable." >&2; exit 1
fi

# ── 4. Copie .env.example → .env (sans écraser) ───────────────
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "INFO : .env créé depuis .env.example — pensez à vérifier les valeurs."
  else
    echo "AVERTISSEMENT : .env et .env.example absents — certaines variables seront vides." >&2
  fi
fi

# ── 5. Démarrage ──────────────────────────────────────────────
echo ""
echo "==> Démarrage HealthAI en mode '$PROFILE'..."
docker compose -f docker-compose.yml -f "$OVERRIDE" up -d --build

# ── 6. Attente healthchecks (postgres + api) ──────────────────
TIMEOUT=900   # 15 minutes max
WARN_AT=600   # alerte à 10 minutes
INTERVAL=5

echo ""
echo "==> Attente que postgres et api soient healthy (timeout ${TIMEOUT}s)..."

wait_healthy() {
  local service="$1"
  local elapsed=0
  local warned=false

  while true; do
    local status
    status=$(docker inspect --format='{{.State.Health.Status}}' "healthai_${service}" 2>/dev/null || echo "absent")

    if [ "$status" = "healthy" ]; then
      echo "    [OK] $service healthy"
      return 0
    fi

    if [ "$elapsed" -ge "$TIMEOUT" ]; then
      echo "ERREUR : $service non healthy après ${TIMEOUT}s." >&2
      return 1
    fi

    if [ "$elapsed" -ge "$WARN_AT" ] && [ "$warned" = false ]; then
      echo "AVERTISSEMENT : démarrage > 10 min — objectif cahier des charges dépassé." >&2
      warned=true
    fi

    sleep "$INTERVAL"
    elapsed=$((elapsed + INTERVAL))
  done
}

wait_healthy postgres
wait_healthy api

# ── 7. Récapitulatif ──────────────────────────────────────────
END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))

echo ""
echo "================================================"
echo " HealthAI démarré en mode '$PROFILE' — ${ELAPSED}s"
echo "================================================"
echo " Frontend        : http://localhost:3000"
echo " API REST        : http://localhost:8000"
echo " AI API          : http://localhost:8002"
echo " Recommandations : http://localhost:8001"
echo " Publications    : http://localhost:8004"
echo " MinIO console   : http://localhost:9001"
echo " Prometheus      : http://localhost:9090"
if [ "$PROFILE" != "perf" ]; then
  echo " Grafana         : http://localhost:3003"
  echo " Metabase        : http://localhost:3001"
  echo " Maquettes       : http://localhost:3002"
fi
echo "================================================"

if [ "$ELAPSED" -gt 600 ]; then
  echo ""
  echo "/!\\ ATTENTION : démarrage en ${ELAPSED}s > 10 min (objectif cahier des charges)."
fi
