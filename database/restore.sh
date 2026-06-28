#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# HealthAI Coach — Script de restauration PostgreSQL
# Fichier  : restore.sh
# Auteure  : Hanane
#
# Fonctionnement :
#   - Restaure une sauvegarde .dump produite par backup.sh
#   - Valide l'intégrité du fichier avant toute opération
#   - Recrée la base cible (DROP + CREATE) pour une restauration propre
#   - Vérifie la cohérence des tables principales après restauration
#
# Utilisation :
#   chmod +x restore.sh
#   ./restore.sh /backups/postgres/healthai_20250520_020000.dump
#   # ou pour restaurer la dernière sauvegarde :
#   ./restore.sh --latest
#
# ⚠️  ATTENTION : la base cible sera SUPPRIMÉE puis RECRÉÉE.
#     Sauvegardez les données courantes avant d'exécuter ce script
#     en production.
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
PG_HOST="${POSTGRES_HOST:-localhost}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DB:-healthai}"
PG_USER="${POSTGRES_USER:-healthai}"
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
LOG_PREFIX="[RESTORE][$(date '+%Y-%m-%d %H:%M:%S')]"

# ─────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ─────────────────────────────────────────────────────────────────
log()  { echo "${LOG_PREFIX} $*"; }
err()  { echo "${LOG_PREFIX} ERREUR : $*" >&2; }
die()  { err "$*"; exit 1; }

usage() {
    echo "Usage : $0 <fichier.dump>"
    echo "        $0 --latest          # restaure la sauvegarde la plus récente"
    exit 1
}

# ─────────────────────────────────────────────────────────────────
# Résolution du fichier à restaurer
# ─────────────────────────────────────────────────────────────────
if [[ $# -eq 0 ]]; then
    usage
fi

if [[ "$1" == "--latest" ]]; then
    DUMP_FILE=$(find "$BACKUP_DIR" -maxdepth 1 -name "healthai_*.dump" | sort | tail -n 1)
    [[ -n "$DUMP_FILE" ]] || die "Aucune sauvegarde trouvée dans $BACKUP_DIR"
    log "Sauvegarde la plus récente sélectionnée : $(basename "$DUMP_FILE")"
else
    DUMP_FILE="$1"
fi

# ─────────────────────────────────────────────────────────────────
# Vérifications préliminaires
# ─────────────────────────────────────────────────────────────────
command -v pg_restore &>/dev/null || die "pg_restore introuvable. Installez postgresql-client."
command -v psql       &>/dev/null || die "psql introuvable. Installez postgresql-client."
[[ -n "${POSTGRES_PASSWORD:-}" ]]  || die "POSTGRES_PASSWORD non défini."
[[ -f "$DUMP_FILE" ]]              || die "Fichier introuvable : $DUMP_FILE"

# ─────────────────────────────────────────────────────────────────
# Étape 1 : validation d'intégrité du fichier
# ─────────────────────────────────────────────────────────────────
log "Étape 1/4 — Validation d'intégrité du fichier dump..."
export PGPASSWORD="$POSTGRES_PASSWORD"

pg_restore --list "$DUMP_FILE" &>/dev/null \
    || { unset PGPASSWORD; die "Le fichier dump est illisible ou corrompu : $DUMP_FILE"; }

TABLE_COUNT=$(pg_restore --list "$DUMP_FILE" | grep -c "TABLE DATA" || true)
log "Fichier valide — ${TABLE_COUNT} table(s) de données détectées."

# ─────────────────────────────────────────────────────────────────
# Étape 2 : confirmation interactive (sécurité)
# ─────────────────────────────────────────────────────────────────
log "Étape 2/4 — Confirmation de la restauration"
echo ""
echo "  ⚠️  ATTENTION : Cette opération va SUPPRIMER et RECRÉER la base '${PG_DB}'."
echo "  Fichier source : $DUMP_FILE"
echo "  Hôte cible     : ${PG_HOST}:${PG_PORT}"
echo ""
read -r -p "  Confirmez-vous la restauration ? [oui/NON] : " CONFIRM

if [[ "$CONFIRM" != "oui" ]]; then
    log "Restauration annulée par l'utilisateur."
    unset PGPASSWORD
    exit 0
fi

# ─────────────────────────────────────────────────────────────────
# Étape 3 : suppression et recréation de la base
# ─────────────────────────────────────────────────────────────────
log "Étape 3/4 — Recréation de la base de données '${PG_DB}'..."

# Connexion à la base postgres (système) pour pouvoir DROP la base cible
psql \
    --host="$PG_HOST" \
    --port="$PG_PORT" \
    --username="$PG_USER" \
    --dbname="postgres" \
    --no-password \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${PG_DB}' AND pid <> pg_backend_pid();" \
    &>/dev/null || true

psql \
    --host="$PG_HOST" \
    --port="$PG_PORT" \
    --username="$PG_USER" \
    --dbname="postgres" \
    --no-password \
    -c "DROP DATABASE IF EXISTS ${PG_DB};" \
    || die "Impossible de supprimer la base '${PG_DB}'"

psql \
    --host="$PG_HOST" \
    --port="$PG_PORT" \
    --username="$PG_USER" \
    --dbname="postgres" \
    --no-password \
    -c "CREATE DATABASE ${PG_DB} OWNER ${PG_USER};" \
    || die "Impossible de créer la base '${PG_DB}'"

log "Base '${PG_DB}' recréée."

# ─────────────────────────────────────────────────────────────────
# Étape 4 : restauration des données
# ─────────────────────────────────────────────────────────────────
log "Étape 4/4 — Restauration des données..."

pg_restore \
    --host="$PG_HOST" \
    --port="$PG_PORT" \
    --username="$PG_USER" \
    --dbname="$PG_DB" \
    --no-password \
    --verbose \
    --exit-on-error \
    "$DUMP_FILE" 2>&1 | grep -E "(restoring|error|ERROR)" | head -40 || true

RESTORE_EXIT=${PIPESTATUS[0]}
unset PGPASSWORD

if [[ $RESTORE_EXIT -ne 0 ]]; then
    die "pg_restore a échoué (code $RESTORE_EXIT). Vérifiez les logs ci-dessus."
fi

# ─────────────────────────────────────────────────────────────────
# Validation d'intégrité post-restauration
# ─────────────────────────────────────────────────────────────────
log "Validation post-restauration..."
export PGPASSWORD="$POSTGRES_PASSWORD"

TABLES_TO_CHECK=("users" "posts" "likes" "comments" "user_profiles")
ALL_OK=true

for TABLE in "${TABLES_TO_CHECK[@]}"; do
    COUNT=$(psql \
        --host="$PG_HOST" --port="$PG_PORT" \
        --username="$PG_USER" --dbname="$PG_DB" \
        --no-password --tuples-only \
        -c "SELECT COUNT(*) FROM ${TABLE};" 2>/dev/null | tr -d ' ' || echo "ERREUR")

    if [[ "$COUNT" == "ERREUR" ]]; then
        err "Table '${TABLE}' introuvable ou inaccessible."
        ALL_OK=false
    else
        log "  ✓ ${TABLE} : ${COUNT} enregistrement(s)"
    fi
done

unset PGPASSWORD

if [[ "$ALL_OK" == "false" ]]; then
    die "Des tables sont manquantes après la restauration. Vérifiez la sauvegarde."
fi

# ─────────────────────────────────────────────────────────────────
# Résumé final
# ─────────────────────────────────────────────────────────────────
log "══════════════════════════════════════════"
log "Restauration terminée avec succès."
log "Base     : $PG_DB"
log "Source   : $DUMP_FILE"
log "Toutes les tables principales sont accessibles."
log "══════════════════════════════════════════"
