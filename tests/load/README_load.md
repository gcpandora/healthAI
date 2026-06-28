# Tests de charge — HealthAI Coach

## Lancement

```bash
# Prérequis : stack démarrée + seed exécuté
pip install locust
locust -f tests/load/locustfile.py --host http://localhost:8000 \
  --users 50 --spawn-rate 5 --run-time 2m --headless
```

## Interprétation des résultats

| Indicateur | Seuil acceptable | Action si dépassé |
|---|---|---|
| Median response time | < 200 ms | Optimiser requêtes SQL ou ajouter index |
| 95th percentile (p95) | < 1 000 ms | Profiler les endpoints lents |
| Failure rate | < 1 % | Vérifier les logs Docker et les timeouts |
| RPS (req/s) | > 20 à 50 users | Augmenter les workers uvicorn |
