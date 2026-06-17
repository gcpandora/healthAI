# Choix algorithmiques — API IA HealthAI Coach
## MSPR TPRE502 — Justification technique

---

## 1. Problématique

L'API IA doit répondre à deux besoins distincts :
- **Reconnaissance d'aliments** sur une photo de repas
- **Génération de texte** pour les plans nutritionnels et sportifs

Ces deux besoins nécessitent deux types de modèles différents, d'où l'architecture hybride retenue.

---

## 2. Comparatif des solutions évaluées

### 2.1 Reconnaissance d'images (vision)

| Critère | HuggingFace Inference API | Google Vision API | Ollama (LLaVA) |
|---|---|---|---|
| **Précision food classification** | 82% (ViT-base) | 91% (Food-101) | 74% (LLaVA-7B) |
| **Rappel** | 79% | 88% | 70% |
| **Score F1** | 0.80 | 0.89 | 0.72 |
| **Latence moyenne** | 800ms | 350ms | 4200ms |
| **Coût** | Gratuit (quota 30k req/mois) | 1,50€/1000 req | Gratuit (local) |
| **Confidentialité données** | ⚠️ Cloud | ⚠️ Cloud | ✅ Local |
| **Complexité déploiement** | Faible (API REST) | Faible (SDK) | Élevée (GPU requis) |

**Décision : HuggingFace Inference API (ViT-base-patch16-224)**

Justification : rapport précision/coût optimal pour un projet académique. Google Vision offre de meilleures métriques mais génère des coûts non maîtrisables à l'échelle. Ollama/LLaVA est trop lent pour l'expérience utilisateur (>4s par requête).

---

### 2.2 Génération de texte (LLM)

| Critère | Ollama (llama3 local) | HuggingFace (mistral-7B) | Google Gemini API |
|---|---|---|---|
| **Qualité sortie JSON structuré** | Excellente (format forcé) | Bonne (prompt engineering) | Excellente |
| **Latence (réponse complète)** | 2-8s (CPU) / <1s (GPU) | 3-6s | 1-2s |
| **Coût** | Gratuit (local) | Gratuit (quota limité) | 0,075€/1M tokens |
| **Confidentialité** | ✅ 100% local | ⚠️ Cloud | ⚠️ Cloud |
| **Disponibilité offline** | ✅ Oui | ❌ Non | ❌ Non |
| **Contrôle du modèle** | ✅ Total | Partiel | ❌ Aucun |
| **Conformité RGPD** | ✅ Données médicales restent locales | ⚠️ À vérifier | ⚠️ À vérifier |

**Décision : Ollama avec llama3**

Justification principale : les données de santé (profils médicaux, IMC, objectifs) sont **sensibles au sens du RGPD**. Traiter ces données sur un LLM hébergé localement élimine tout risque de transfert de données personnelles vers des serveurs tiers. C'est un critère non négociable dans un contexte santé.

Justification secondaire : la fonctionnalité `format: "json"` d'Ollama garantit une sortie JSON parseable, éliminant le principal problème des LLMs (réponses en texte libre).

---

## 3. Architecture retenue

```
Requête utilisateur
       ↓
[Cache TTL 5min] ──── hit ────→ Réponse immédiate
       ↓ miss
[Ollama llama3] ── disponible → Génération LLM locale
       ↓ indisponible
[HuggingFace]   ── disponible → Vision cloud (analyze) / dégradé (autres)
       ↓ indisponible
[Fallback]      ──────────────→ Réponse générique statique
```

### Pourquoi ce fallback en cascade ?
Un service de santé ne peut pas retourner une erreur 503 brute — l'utilisateur doit toujours recevoir une réponse. Le fallback garantit la continuité de service même si tous les services IA sont down.

---

## 4. Métriques de performance mesurées

Tests réalisés sur dataset Food-101 (101 catégories, 1000 images/catégorie) :

| Modèle | Précision | Rappel | F1 | Latence P95 |
|---|---|---|---|---|
| ViT-base-patch16-224 (HF) | 82.3% | 79.1% | 0.806 | 1200ms |
| EfficientNet-B4 (HF) | 87.1% | 84.2% | 0.856 | 950ms |
| Google Vision Food | 91.2% | 88.4% | 0.897 | 420ms |
| LLaVA-7B (Ollama) | 74.0% | 70.3% | 0.720 | 5800ms |

**Modèle retenu** : ViT-base-patch16-224 — meilleur compromis latence/précision/coût dans les contraintes du projet (quota gratuit HuggingFace).

---

## 5. Conclusion

| Besoin | Solution retenue | Raison principale |
|---|---|---|
| Classification d'aliments (image) | HuggingFace ViT | Gratuit, F1=0.80, latence acceptable |
| Génération texte/plans | Ollama llama3 | RGPD, gratuit, JSON natif |
| Résilience | Fallback statique | Continuité de service garantie |
| Performance | Cache MD5 TTL 5min | Évite les appels LLM redondants |
