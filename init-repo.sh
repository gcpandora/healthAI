#!/bin/bash
# ════════════════════════════════════════════════
# Script d'initialisation du repo Git — HealthAI Coach
# Usage : bash init-repo.sh https://github.com/TON_ORG/healthai-coach.git
# ════════════════════════════════════════════════

REMOTE_URL=$1

echo "🏥 Initialisation du repo HealthAI Coach"

# Init Git
git init
git add .
git commit -m "chore: initialisation du repo — structure de base"

# Créer la branche develop
git checkout -b develop

echo ""
echo "✅ Repo initialisé avec la branche 'develop'"
echo ""

if [ -n "$REMOTE_URL" ]; then
    git remote add origin "$REMOTE_URL"
    git push -u origin develop
    echo "✅ Code poussé sur $REMOTE_URL"
fi

echo ""
echo "📋 Prochaines étapes :"
echo "  1. Créer le repo sur GitHub (vide, sans README)"
echo "  2. bash init-repo.sh https://github.com/TON_ORG/healthai-coach.git"
echo "  3. Sur GitHub : Settings → Branches → Protéger 'main' et 'develop'"
echo "  4. Inviter les membres de l'équipe dans Settings → Collaborators"
echo ""
echo "🌿 Convention de branches :"
echo "  feature/prenom-description"
echo "  fix/prenom-description"
echo "  Jamais de push direct sur main ou develop"
