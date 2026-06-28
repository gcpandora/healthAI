#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# backup.sh — Sauvegarde PostgreSQL avec horodatage et rotation 7 jours
# Usage : ./scripts/backup.sh
# Variables d'environnement requises : POSTGRES_USER, POSTGRES_DB
# Variables optionnelles : POSTGRES_HOST (défaut: localhost), BACKUP_DIR
# ─────────────────────────────────────────────────────────────────────────────

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:?Variable POSTGRES_USER non définie}"
POSTGRES_DB="${POSTGRES_DB:?Variable POSTGRES_DB non définie}"
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
RETENTION_DAYS=7

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"

mkdir -p "$BACKUP_DIR"

echo "[$(date '+%H:%M:%S')] Démarrage sauvegarde PostgreSQL..."
echo "  Base     : $POSTGRES_DB"
echo "  Hôte     : $POSTGRES_HOST:$POSTGRES_PORT"
echo "  Fichier  : $BACKUP_FILE"

pg_dump \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --format=custom \
  --compress=9 \
  --no-password \
  --dbname="$POSTGRES_DB" \
  --file="$BACKUP_FILE"

SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
echo "[$(date '+%H:%M:%S')] ✔ Sauvegarde créée : $BACKUP_FILE ($SIZE)"

# Rotation : suppression des fichiers de plus de RETENTION_DAYS jours
echo "[$(date '+%H:%M:%S')] Rotation : suppression des sauvegardes > ${RETENTION_DAYS} jours..."
DELETED=$(find "$BACKUP_DIR" -name "${POSTGRES_DB}_*.dump" -mtime +"$RETENTION_DAYS" -print -delete | wc -l)
echo "[$(date '+%H:%M:%S')] ✔ $DELETED fichier(s) supprimé(s)"

# Inventaire
echo ""
echo "Sauvegardes disponibles dans $BACKUP_DIR :"
find "$BACKUP_DIR" -name "${POSTGRES_DB}_*.dump" -printf "  %f  (%s octets)\n" | sort
