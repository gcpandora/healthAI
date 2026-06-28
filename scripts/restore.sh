#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# restore.sh — Restauration PostgreSQL + vérification du nombre de tables
# Usage : ./scripts/restore.sh <fichier.dump>
# Variables d'environnement requises : POSTGRES_USER, POSTGRES_DB
# ─────────────────────────────────────────────────────────────────────────────

BACKUP_FILE="${1:-}"
if [[ -z "$BACKUP_FILE" ]]; then
  echo "Usage : $0 <fichier.dump>"
  echo "Exemple : $0 /backups/postgres/healthai_db_20250101_120000.dump"
  exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "ERREUR : fichier introuvable : $BACKUP_FILE"
  exit 1
fi

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:?Variable POSTGRES_USER non définie}"
POSTGRES_DB="${POSTGRES_DB:?Variable POSTGRES_DB non définie}"

echo "[$(date '+%H:%M:%S')] Restauration de : $BACKUP_FILE"
echo "  Base     : $POSTGRES_DB"
echo "  Hôte     : $POSTGRES_HOST:$POSTGRES_PORT"
echo ""
echo "ATTENTION : cette opération écrase les données existantes."
echo "Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler..."
read -r

echo "[$(date '+%H:%M:%S')] Suppression et recréation de la base..."
psql \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --no-password \
  --command="DROP DATABASE IF EXISTS ${POSTGRES_DB};" \
  postgres

psql \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --no-password \
  --command="CREATE DATABASE ${POSTGRES_DB};" \
  postgres

echo "[$(date '+%H:%M:%S')] Restauration en cours..."
pg_restore \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --no-password \
  --dbname="$POSTGRES_DB" \
  --verbose \
  "$BACKUP_FILE" 2>&1 | grep -E "^pg_restore:|error|warning" || true

# Vérification : compte le nombre de tables restaurées
TABLE_COUNT=$(psql \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --no-password \
  --dbname="$POSTGRES_DB" \
  --tuples-only \
  --command="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")

TABLE_COUNT=$(echo "$TABLE_COUNT" | tr -d ' ')

echo ""
echo "[$(date '+%H:%M:%S')] ✔ Restauration terminée"
echo "  Tables restaurées : $TABLE_COUNT"

if [[ "$TABLE_COUNT" -eq 0 ]]; then
  echo "ERREUR : aucune table restaurée — vérifiez le fichier de sauvegarde."
  exit 1
fi

echo "  Restauration OK ✔"
