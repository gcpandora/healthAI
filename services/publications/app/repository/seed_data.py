"""
Jeu de données de démonstration.
Sera remplacé par le seed SQL d'Hanane (script seed PostgreSQL).
"""
from datetime import datetime, timezone, timedelta

_now = datetime.now(timezone.utc)


def _iso(minutes_ago: int) -> str:
    return (_now - timedelta(minutes=minutes_ago)).isoformat()


PROFILES = [
    {"user_id": "11111111-1111-1111-1111-111111111111", "display_name": "Tojo",
     "avatar_url": "http://localhost:9000/healthai-media/avatars/tojo.jpg",
     "bio": "Backend dev · API publications",
     "created_at": _iso(5000), "updated_at": _iso(100)},
    {"user_id": "22222222-2222-2222-2222-222222222222", "display_name": "Hélie",
     "avatar_url": "http://localhost:9000/healthai-media/avatars/helie.jpg",
     "bio": "Mobile dev · React Native",
     "created_at": _iso(4800), "updated_at": _iso(200)},
    {"user_id": "33333333-3333-3333-3333-333333333333", "display_name": "Hanane",
     "avatar_url": None, "bio": "Data · PostgreSQL & MinIO",
     "created_at": _iso(4600), "updated_at": _iso(300)},
]

POSTS = [
    {"id": "aaaaaaaa-0000-0000-0000-000000000001",
     "user_id": "22222222-2222-2222-2222-222222222222",
     "content": "Première séance running de la semaine, 5km bouclés !",
     "media_urls": ["http://localhost:9000/healthai-media/posts/run1.jpg"],
     "created_at": _iso(120), "updated_at": _iso(120)},
    {"id": "aaaaaaaa-0000-0000-0000-000000000002",
     "user_id": "11111111-1111-1111-1111-111111111111",
     "content": "Objectif sommeil atteint : 8h cette nuit.",
     "media_urls": [],
     "created_at": _iso(90), "updated_at": _iso(90)},
    {"id": "aaaaaaaa-0000-0000-0000-000000000003",
     "user_id": "33333333-3333-3333-3333-333333333333",
     "content": "Nouvelle recette healthy testée ce midi 🥗",
     "media_urls": ["http://localhost:9000/healthai-media/posts/meal1.jpg",
                    "http://localhost:9000/healthai-media/posts/meal2.jpg"],
     "created_at": _iso(45), "updated_at": _iso(45)},
]

LIKES = [
    {"post_id": "aaaaaaaa-0000-0000-0000-000000000001",
     "user_id": "11111111-1111-1111-1111-111111111111", "created_at": _iso(110)},
    {"post_id": "aaaaaaaa-0000-0000-0000-000000000001",
     "user_id": "33333333-3333-3333-3333-333333333333", "created_at": _iso(100)},
    {"post_id": "aaaaaaaa-0000-0000-0000-000000000003",
     "user_id": "22222222-2222-2222-2222-222222222222", "created_at": _iso(40)},
]

COMMENTS = [
    {"id": "cccccccc-0000-0000-0000-000000000001",
     "post_id": "aaaaaaaa-0000-0000-0000-000000000001",
     "user_id": "33333333-3333-3333-3333-333333333333",
     "content": "Bravo ! On court ensemble la prochaine fois ?", "created_at": _iso(80)},
    {"id": "cccccccc-0000-0000-0000-000000000002",
     "post_id": "aaaaaaaa-0000-0000-0000-000000000003",
     "user_id": "11111111-1111-1111-1111-111111111111",
     "content": "Ça donne faim, la recette stp !", "created_at": _iso(30)},
]
