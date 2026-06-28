#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# HealthAI Coach — Script de sauvegarde PostgreSQL
# Fichier  : backup.sh
# Auteure  : Hanane
#
# Fonctionnement :
#   - Exécute un pg_dump complet de la base HealthAI
#   - Horodate le fichier de sortie (YYYYMMDD_HHMMSS)
#   - Stocke les dumps dans /backups/postgres/
#   - Conserve uniquement les 7 derniers fichiers (rotation automatique)
#   - Retourne un code de sortie non-nul en cas d'erreur
#
# Utilisation :
#   chmod +x backup.sh
#   ./backup.sh
#   # ou via cron : 0 2 * * * /opt/healthai/backup.sh >> /var/log/healthai_backup.log 2>&1
#
# Variables d'environnement attendues (ou lues depuis .env) :
#   POSTGRES_HOST      (défaut : localhost)
#   POSTGRES_PORT      (défaut : 5432)
#   POSTGRES_DB        (défaut : healthai)
#   POSTGRES_USER      (défaut : healthai)
#   POSTGRES_PASSWORD
#   BACKUP_DIR         (défaut : /backups/postgres)
#   BACKUP_RETENTION   (défaut : 7)
# ════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# Chargement du .env si présent (hors container)
# ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../../.env"
if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    set -a; source "$ENV_FILE"; set +a
fi

# ─────────────────────────────────────────────────────────────────
# Configuration (valeurs par défaut si variables absentes)
# ─────────────────────────────────────────────────────────────────
PG_HOST="${POSTGRES_HOST:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DB:-healthai}"
PG_USER="${POSTGRES_USER:-healthai}"
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
RETENTION="${BACKUP_RETENTION:-7}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/healthai_${TIMESTAMP}.dump"
LOG_PREFIX="[BACKUP][$(date '+%Y-%m-%d %H:%M:%S')]"

# ─────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ─────────────────────────────────────────────────────────────────
log()  { echo "${LOG_PREFIX} $*"; }
err()  { echo "${LOG_PREFIX} ERREUR : $*" >&2; }
die()  { err "$*"; exit 1; }

# ─────────────────────────────────────────────────────────────────
# Vérifications préliminaires
# ─────────────────────────────────────────────────────────────────
command -v pg_dump &>/dev/null || die "pg_dump introuvable. Installez postgresql-client."
[[ -n "${POSTGRES_PASSWORD:-}" ]]  || die "POSTGRES_PASSWORD non défini."

mkdir -p "$BACKUP_DIR" || die "Impossible de créer le répertoire $BACKUP_DIR"

# ─────────────────────────────────────────────────────────────────
# Sauvegarde (format custom pg_dump — compressé, restaurable
# partiellement avec pg_restore)
# ─────────────────────────────────────────────────────────────────
log "Démarrage de la sauvegarde → $BACKUP_FILE"

export PGPASSWORD="$POSTGRES_PASSWORD"

pg_dump \
    --host="$PG_HOST" \
    --port="$PG_PORT" \
    --username="$PG_USER" \
    --dbname="$PG_DB" \
    --format=custom \
    --compress=9 \
    --no-password \
    --file="$BACKUP_FILE"

DUMP_EXIT=$?
unset PGPASSWORD

if [[ $DUMP_EXIT -ne 0 ]]; then
    rm -f "$BACKUP_FILE"
    die "pg_dump a échoué (code $DUMP_EXIT). Fichier temporaire supprimé."
fi

BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
log "Sauvegarde réussie — taille : ${BACKUP_SIZE}"

# ─────────────────────────────────────────────────────────────────
# Rotation : on garde les N derniers fichiers .dump
# ─────────────────────────────────────────────────────────────────
log "Rotation des sauvegardes (conservation : ${RETENTION} derniers fichiers)"

DUMP_COUNT=$(find "$BACKUP_DIR" -maxdepth 1 -name "healthai_*.dump" | wc -l)

if [[ $DUMP_COUNT -gt $RETENTION ]]; then
    TO_DELETE=$(( DUMP_COUNT - RETENTION ))
    find "$BACKUP_DIR" -maxdepth 1 -name "healthai_*.dump" \
        | sort \
        | head -n "$TO_DELETE" \
        | while read -r OLD_FILE; do
            log "Suppression ancienne sauvegarde : $(basename "$OLD_FILE")"
            rm -f "$OLD_FILE"
        done
fi

# ─────────────────────────────────────────────────────────────────
# Vérification d'intégrité rapide
# ─────────────────────────────────────────────────────────────────
log "Vérification d'intégrité du fichier dump..."
export PGPASSWORD="$POSTGRES_PASSWORD"

pg_restore --list "$BACKUP_FILE" &>/dev/null \
    && log "Intégrité OK — le fichier est lisible par pg_restore." \
    || { unset PGPASSWORD; die "Le fichier dump semble corrompu !"; }

unset PGPASSWORD

# ─────────────────────────────────────────────────────────────────
# Résumé final
# ─────────────────────────────────────────────────────────────────
log "══════════════════════════════════════════"
log "Sauvegarde terminée avec succès."
log "Fichier   : $BACKUP_FILE"
log "Taille    : $BACKUP_SIZE"
log "Rétention : $RETENTION fichier(s) maximum"
log "══════════════════════════════════════════"
