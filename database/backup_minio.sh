#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# HealthAI Coach — Script de sauvegarde MinIO (buckets)
# Fichier  : backup_minio.sh
# Auteure  : Hanane
#
# Fonctionnement :
#   - Utilise mc mirror pour copier le contenu du bucket healthai-media
#     vers un volume local horodaté
#   - Vérifie l'intégrité du contenu après la copie (comptage de fichiers)
#   - Conserve les N dernières sauvegardes (rotation)
#
# Utilisation :
#   chmod +x backup_minio.sh
#   ./backup_minio.sh
#   # ou via cron : 0 3 * * * /opt/healthai/backup_minio.sh >> /var/log/healthai_minio_backup.log 2>&1
#
# Variables d'environnement attendues (ou lues depuis .env) :
#   MINIO_ROOT_USER       (défaut : minioadmin)
#   MINIO_ROOT_PASSWORD   (défaut : minioadmin)
#   MINIO_ENDPOINT        (défaut : http://localhost:9000)
#   MINIO_BUCKET          (défaut : healthai-media)
#   MINIO_BACKUP_DIR      (défaut : /backups/minio)
#   MINIO_BACKUP_RETENTION (défaut : 7)
# ════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# Chargement du .env si présent
# ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../../.env"
if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    set -a; source "$ENV_FILE"; set +a
fi

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────
MINIO_USER="${MINIO_ROOT_USER:-minioadmin}"
MINIO_PASS="${MINIO_ROOT_PASSWORD:-minioadmin}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://localhost:9000}"
MINIO_BUCKET="${MINIO_BUCKET:-healthai-media}"
BACKUP_BASE_DIR="${MINIO_BACKUP_DIR:-/backups/minio}"
RETENTION="${MINIO_BACKUP_RETENTION:-7}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${BACKUP_BASE_DIR}/healthai-media_${TIMESTAMP}"
LOG_PREFIX="[MINIO-BACKUP][$(date '+%Y-%m-%d %H:%M:%S')]"

# ─────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ─────────────────────────────────────────────────────────────────
log()  { echo "${LOG_PREFIX} $*"; }
err()  { echo "${LOG_PREFIX} ERREUR : $*" >&2; }
die()  { err "$*"; exit 1; }

# ─────────────────────────────────────────────────────────────────
# Vérifications préliminaires
# ─────────────────────────────────────────────────────────────────
command -v mc &>/dev/null || die "'mc' (MinIO Client) introuvable. Installez-le : https://min.io/docs/minio/linux/reference/minio-mc.html"

mkdir -p "$BACKUP_DIR" || die "Impossible de créer le répertoire $BACKUP_DIR"

# ─────────────────────────────────────────────────────────────────
# Configuration de l'alias mc (temporaire, sans fichier de config persistant)
# ─────────────────────────────────────────────────────────────────
export MC_CONFIG_DIR="/tmp/mc_healthai_$$"
mkdir -p "$MC_CONFIG_DIR"
trap 'rm -rf "$MC_CONFIG_DIR"' EXIT

log "Connexion à MinIO : $MINIO_ENDPOINT"

mc alias set healthai "$MINIO_ENDPOINT" "$MINIO_USER" "$MINIO_PASS" --quiet \
    || die "Impossible de se connecter à MinIO. Vérifiez MINIO_ENDPOINT et les credentials."

# ─────────────────────────────────────────────────────────────────
# Vérification que le bucket existe
# ─────────────────────────────────────────────────────────────────
mc ls "healthai/${MINIO_BUCKET}" &>/dev/null \
    || die "Bucket '${MINIO_BUCKET}' introuvable sur MinIO."

# Comptage des objets source avant sauvegarde
SOURCE_COUNT=$(mc ls --recursive "healthai/${MINIO_BUCKET}" 2>/dev/null | wc -l)
log "Objets dans le bucket source : ${SOURCE_COUNT}"

# ─────────────────────────────────────────────────────────────────
# Sauvegarde via mc mirror
# mc mirror copie de manière idempotente : seuls les fichiers
# absents ou modifiés sont transférés
# ─────────────────────────────────────────────────────────────────
log "Démarrage du mirror → $BACKUP_DIR"

mc mirror \
    --watch=false \
    --overwrite \
    "healthai/${MINIO_BUCKET}" \
    "$BACKUP_DIR" \
    || die "mc mirror a échoué. Sauvegarde incomplète dans $BACKUP_DIR"

log "Mirror terminé."

# ─────────────────────────────────────────────────────────────────
# Vérification d'intégrité : comparaison du nombre d'objets
# ─────────────────────────────────────────────────────────────────
log "Vérification d'intégrité..."

LOCAL_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)

if [[ "$LOCAL_COUNT" -eq "$SOURCE_COUNT" ]]; then
    log "Intégrité OK — ${LOCAL_COUNT} fichier(s) copiés sur ${SOURCE_COUNT} attendus."
else
    err "Écart détecté : ${LOCAL_COUNT} fichiers locaux vs ${SOURCE_COUNT} dans le bucket."
    err "La sauvegarde peut être incomplète. Répertoire conservé : $BACKUP_DIR"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────
# Rotation : conserver les N derniers répertoires de sauvegarde
# ─────────────────────────────────────────────────────────────────
log "Rotation des sauvegardes (conservation : ${RETENTION} dernières)"

BACKUP_COUNT=$(find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "healthai-media_*" | wc -l)

if [[ $BACKUP_COUNT -gt $RETENTION ]]; then
    TO_DELETE=$(( BACKUP_COUNT - RETENTION ))
    find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "healthai-media_*" \
        | sort \
        | head -n "$TO_DELETE" \
        | while read -r OLD_DIR; do
            log "Suppression ancienne sauvegarde : $(basename "$OLD_DIR")"
            rm -rf "$OLD_DIR"
        done
fi

# ─────────────────────────────────────────────────────────────────
# Résumé
# ─────────────────────────────────────────────────────────────────
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

log "══════════════════════════════════════════"
log "Sauvegarde MinIO terminée avec succès."
log "Répertoire : $BACKUP_DIR"
log "Taille     : $BACKUP_SIZE"
log "Fichiers   : $LOCAL_COUNT"
log "Rétention  : $RETENTION répertoire(s) maximum"
log "══════════════════════════════════════════"
