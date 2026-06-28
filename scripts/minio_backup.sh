#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# minio_backup.sh — Miroir MinIO bucket → répertoire local + vérification
# Usage : ./scripts/minio_backup.sh
# Variables d'environnement requises : MINIO_ENDPOINT, MINIO_ACCESS_KEY,
#   MINIO_SECRET_KEY, MINIO_BUCKET (défaut: healthai-media)
# ─────────────────────────────────────────────────────────────────────────────

MINIO_ENDPOINT="${MINIO_ENDPOINT:-localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:?Variable MINIO_ACCESS_KEY non définie}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:?Variable MINIO_SECRET_KEY non définie}"
MINIO_BUCKET="${MINIO_BUCKET:-healthai-media}"
BACKUP_DIR="${BACKUP_DIR:-/backups/minio}"
ALIAS="healthai-backup-$$"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEST="${BACKUP_DIR}/${MINIO_BUCKET}_${TIMESTAMP}"

mkdir -p "$DEST"

echo "[$(date '+%H:%M:%S')] Configuration de l'alias MinIO..."
mc alias set "$ALIAS" "http://${MINIO_ENDPOINT}" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" --api S3v4

echo "[$(date '+%H:%M:%S')] Miroir du bucket : ${MINIO_BUCKET} → ${DEST}"
mc mirror "${ALIAS}/${MINIO_BUCKET}" "$DEST"

# Vérification : comptage des fichiers dans le bucket vs la destination
REMOTE_COUNT=$(mc ls --recursive "${ALIAS}/${MINIO_BUCKET}" 2>/dev/null | wc -l)
LOCAL_COUNT=$(find "$DEST" -type f | wc -l)

echo ""
echo "[$(date '+%H:%M:%S')] Vérification :"
echo "  Fichiers bucket  : $REMOTE_COUNT"
echo "  Fichiers locaux  : $LOCAL_COUNT"

mc alias rm "$ALIAS" 2>/dev/null || true

if [[ "$REMOTE_COUNT" -ne "$LOCAL_COUNT" ]]; then
  echo "ERREUR : écart entre bucket ($REMOTE_COUNT) et local ($LOCAL_COUNT)"
  exit 1
fi

echo "  ✔ Miroir complet — $LOCAL_COUNT fichier(s) sauvegardé(s) dans $DEST"
