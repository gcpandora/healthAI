from fastapi import FastAPI

app = FastAPI(title="HealthAI Publications API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "publications-api"}


@app.get("/publications")
def list_publications():
    # TODO (Tojo) : implémenter la logique métier
    return {"publications": []}
