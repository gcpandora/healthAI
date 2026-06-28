#!/usr/bin/env bash
set -euo pipefail

echo "================================================"
echo " HealthAI — RESET COMPLET"
echo " Cette action va supprimer tous les containers,"
echo " volumes et données persistées (postgres, mongo,"
echo " ollama, minio, prometheus, grafana)."
echo "================================================"
echo ""
read -r -p "Confirmer le reset ? [oui/N] : " CONFIRM

if [ "$CONFIRM" != "oui" ]; then
  echo "Reset annulé."
  exit 0
fi

echo ""
echo "==> Arrêt et suppression des containers + volumes..."
docker compose -f docker-compose.yml down --volumes --remove-orphans

echo ""
echo "==> Reset terminé."
echo ""
read -r -p "Relancer en mode offline (données de démo) ? [O/n] : " RELAUNCH

case "${RELAUNCH:-O}" in
  O|o|oui|yes|"")
    echo ""
    exec ./start.sh offline
    ;;
  *)
    echo "Pour relancer manuellement : ./start.sh [full|offline|perf]"
    ;;
esac
