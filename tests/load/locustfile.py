"""
Scénario de charge HealthAI Coach — 50 utilisateurs simultanés
Cibles : API :8000 (auth, profil) + publications-api :8004 (posts, like)
Lancement : locust -f tests/load/locustfile.py --host http://localhost:8000
"""

import json
import random

from locust import HttpUser, between, task


SEED_USERS = [
    {"email": "alice@healthai.demo",  "password": "Demo1234!"},
    {"email": "bob@healthai.demo",    "password": "Demo1234!"},
    {"email": "claire@healthai.demo", "password": "Demo1234!"},
    {"email": "david@healthai.demo",  "password": "Demo1234!"},
    {"email": "emma@healthai.demo",   "password": "Demo1234!"},
    {"email": "felix@healthai.demo",  "password": "Demo1234!"},
    {"email": "grace@healthai.demo",  "password": "Demo1234!"},
    {"email": "hugo@healthai.demo",   "password": "Demo1234!"},
    {"email": "iris@healthai.demo",   "password": "Demo1234!"},
    {"email": "jules@healthai.demo",  "password": "Demo1234!"},
]

POST_CONTENTS = [
    "Test de charge — post automatique #{n} 🏃",
    "Séance cardio simulée — load test #{n} 💪",
    "Objectif du jour atteint — stress test #{n} 🎯",
]

PUB_API_HOST = "http://localhost:8004"


class HealthAIUser(HttpUser):
    """Utilisateur simulé — alterne entre les deux APIs."""

    wait_time = between(0.5, 2.0)
    token: str = ""
    user_id: str = ""
    post_ids: list = []

    def on_start(self):
        """Login et récupération du JWT au démarrage de chaque utilisateur."""
        creds = random.choice(SEED_USERS)
        with self.client.post(
            "/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
            catch_response=True,
            name="/auth/login",
        ) as r:
            if r.status_code == 200:
                data = r.json()
                self.token = data.get("access_token", "")
                self.user_id = data.get("user_id", "")
                r.success()
            else:
                r.failure(f"Login échoué ({r.status_code})")

    def _pub_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    # ── Tâches API principale :8000 ────────────────────────────────────────

    @task(3)
    def list_posts_pub(self):
        """Liste des posts via publications-api."""
        with self.client.get(
            PUB_API_HOST + "/posts?limit=20",
            headers=self._pub_headers(),
            catch_response=True,
            name="GET /posts (pub)",
        ) as r:
            if r.status_code == 200:
                data = r.json()
                ids = [p["id"] for p in data.get("items", [])]
                if ids:
                    self.post_ids = ids
                r.success()
            else:
                r.failure(f"list_posts {r.status_code}")

    @task(2)
    def create_post(self):
        """Création d'un post."""
        if not self.token:
            return
        content = random.choice(POST_CONTENTS).replace(
            "#{n}", str(random.randint(1, 9999))
        )
        with self.client.post(
            PUB_API_HOST + "/posts",
            json={"content": content, "media_urls": []},
            headers=self._pub_headers(),
            catch_response=True,
            name="POST /posts (pub)",
        ) as r:
            if r.status_code == 201:
                self.post_ids.append(r.json()["id"])
                r.success()
            else:
                r.failure(f"create_post {r.status_code}")

    @task(2)
    def like_post(self):
        """Like sur un post aléatoire."""
        if not self.token or not self.post_ids:
            return
        pid = random.choice(self.post_ids)
        with self.client.post(
            PUB_API_HOST + f"/posts/{pid}/like",
            headers=self._pub_headers(),
            catch_response=True,
            name="POST /posts/{id}/like (pub)",
        ) as r:
            if r.status_code in (200, 201):
                r.success()
            else:
                r.failure(f"like {r.status_code}")

    @task(1)
    def health_check(self):
        """Vérification de santé de l'API principale."""
        self.client.get("/health", name="GET /health")
