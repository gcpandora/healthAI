FROM python:3.11-slim
 
WORKDIR /app
 
# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
 
# Installer les dépendances Python EN PREMIER (layer cacheable)
# Le bind-mount ./services/etl:/app en dev écrase /app mais PAS
# /usr/local/lib — les packages pip restent accessibles.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copier le code source dans l'image
# (utile pour docker compose run, CI, ou sans bind-mount)
COPY . .
 
# Créer les dossiers attendus par les scripts
# En prod/CI ces dossiers sont dans l'image.
# En dev le bind-mount les fournit depuis l'hôte.
RUN mkdir -p data/raw data/clean_bdd data/clean_ml rapport logs
 
# Le pipeline se lance depuis /app/pipelines/
# PYTHONPATH=/app permet les imports absolus depuis services/etl/
ENV PYTHONPATH=/app
 
CMD ["python", "/app/pipelines/run_pipeline.py"]
