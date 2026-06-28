#!/usr/bin/env python3
"""
Seed de démonstration HealthAI Coach
10 utilisateurs · 30 posts · 20 médias MinIO fictifs · likes et commentaires croisés
Idempotent : utilise INSERT ... ON CONFLICT DO NOTHING
Usage : DATABASE_URL=postgresql://... python seed.py
"""

import os
import uuid
import hashlib
import random
import sys
from datetime import datetime, timezone, timedelta

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("ERREUR : psycopg2 manquant. Installez-le via pip install psycopg2-binary")
    sys.exit(1)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERREUR : variable d'environnement DATABASE_URL non définie.")
    sys.exit(1)


def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


def now_offset(days: int = 0, hours: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days, hours=hours)
    return dt.isoformat()


USERS = [
    {"email": "alice@healthai.demo", "username": "alice",   "display_name": "Alice Martin",    "bio": "Coach nutrition 🥗"},
    {"email": "bob@healthai.demo",   "username": "bob",     "display_name": "Bob Dupont",      "bio": "Fan de running 🏃"},
    {"email": "claire@healthai.demo","username": "claire",  "display_name": "Claire Leroy",    "bio": "Yoga & bien-être 🧘"},
    {"email": "david@healthai.demo", "username": "david",   "display_name": "David Morel",     "bio": "Crossfit addict 💪"},
    {"email": "emma@healthai.demo",  "username": "emma",    "display_name": "Emma Bernard",    "bio": "Cycliste passionnée 🚴"},
    {"email": "felix@healthai.demo", "username": "felix",   "display_name": "Félix Thomas",    "bio": "Natation & triathlon 🏊"},
    {"email": "grace@healthai.demo", "username": "grace",   "display_name": "Grace Petit",     "bio": "Pilates & stretching 🤸"},
    {"email": "hugo@healthai.demo",  "username": "hugo",    "display_name": "Hugo Richard",    "bio": "Musculation 🏋️"},
    {"email": "iris@healthai.demo",  "username": "iris",    "display_name": "Iris Simon",      "bio": "Randonnée & montagne ⛰️"},
    {"email": "jules@healthai.demo", "username": "jules",   "display_name": "Jules Laurent",   "bio": "Basketball & cardio 🏀"},
]

POST_CONTENTS = [
    "Séance de cardio ce matin — 45 minutes de vélo d'appartement. Je me sens au top ! 🚴",
    "Nouveau record personnel au squat : 120 kg ! Merci à mon coach pour le programme. 💪",
    "Smoothie du matin : banane, épinards, protéines de chanvre. Une bombe nutritive ! 🥤",
    "La marche rapide le soir, c'est underrated. 30 minutes et je dors comme un bébé. 😴",
    "Objectif semaine atteint : 3 séances de musculation + 2 runs. Je suis fier. 🎯",
    "Astuce récup : bain froid après l'effort. Difficile au début, mais les résultats parlent ! 🧊",
    "Mon plan repas de la semaine est prêt. Macro équilibrée : 40% glucides, 30% protéines. 📊",
    "Première sortie trail de la saison. 10 km en montagne, magnifique ! 🏔️",
    "Résultat bilan santé : tension parfaite, cholestérol OK. Le sport paye vraiment. ✅",
    "Yoga du dimanche matin — séquence salutation au soleil. 1h de pure sérénité. 🧘",
    "Petite victoire : j'ai refusé le dessert au resto. Mon cerveau a dit non spontanément ! 🙌",
    "Semaine difficile, mais j'ai quand même fait mes 3 séances. La régularité avant tout. 💯",
    "Découverte du HIIT : 20 minutes et je suis épuisé comme après 1h de cardio. Bluffant ! ⚡",
    "Préparation marathon dans 3 mois. Programme 16 semaines lancé. Let's go ! 🏃‍♂️",
    "Essai de la boxe thaï aujourd'hui. Technique, cardio, coordination — j'adore ! 🥊",
    "Hydratation : j'ai enfin atteint mon objectif 2L/jour. Différence énorme sur l'énergie. 💧",
    "Résumé de ma semaine fitness : 28 km de course, 3 séances muscu, 2 vélos. Pas mal ! 📈",
    "Recette protéinée : poulet grillé, quinoa, avocat, légumes vapeur. Simple et efficace. 🍽️",
    "Test des bandes élastiques pour la mobilité. Game changer pour mes étirements. 🎯",
    "Mon application préférée pour suivre mes macros : HealthAI Coach. Super précis ! 📱",
    "Premier 10 km sous 50 minutes ! Un objectif que je poursuivais depuis 6 mois. 🎉",
    "La récupération active c'est sous-estimé. Marche légère le lendemain = moins de courbatures. 🚶",
    "Partage de mon échauffement du matin : 10 min de mobilité articulaire. Indispensable ! 🌅",
    "Semaine de décharge après 4 semaines intensives. Mon corps dit merci. 🛌",
    "Cuisine batch cooking du dimanche : 5 repas préparés pour la semaine. Efficacité max ! 👨‍🍳",
    "Objectif janvier : perdre 3 kg tout en maintenant la masse musculaire. C'est parti ! 🎯",
    "Essai du rameur ce matin. Cardio + dos + bras : l'exercice complet par excellence. 🚣",
    "Mon rituel du soir : 20 minutes de stretching. Ça change vraiment la qualité du sommeil. 🌙",
    "Bilan annuel : -8 kg, +5 kg de muscle, -3 cm de tour de taille. L'effort paye. 📊",
    "Défi du mois : 30 jours de planche abdominale. Qui m'accompagne ? 💪🔥",
]

COMMENT_TEMPLATES = [
    "Super motivation, continue comme ça ! 🔥",
    "Impressionnant ! Tu m'inspires vraiment.",
    "Merci pour le partage, j'essaie ça demain.",
    "Quelle progression ! Bravo 👏",
    "Je fais pareil, c'est vraiment efficace.",
    "Tu as un programme à partager ?",
    "C'est exactement ce qu'il me fallait pour me motiver.",
    "Respect pour la régularité ! 💯",
    "J'adore ce type de contenu sur HealthAI 😄",
    "Ça me donne envie de reprendre le sport !",
]

MINIO_MEDIA_URLS = [
    f"http://minio:9000/healthai-media/demo/media_{i:02d}.jpg"
    for i in range(1, 21)
]


def run():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    print("── Insertion des utilisateurs (10) ──────────────────")
    user_ids = []
    for u in USERS:
        uid = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO users (id, email, username, password_hash, age, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET username = EXCLUDED.username
            RETURNING id
            """,
            (uid, u["email"], u["username"], hash_password("Demo1234!"), 28, "other"),
        )
        row = cur.fetchone()
        user_ids.append(str(row[0]))
        print(f"  ✔ {u['username']} ({row[0]})")

    print("\n── Insertion des profils utilisateurs ───────────────")
    for i, u in enumerate(USERS):
        cur.execute(
            """
            INSERT INTO user_profiles (user_id, display_name, bio, avatar_url)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
            """,
            (
                user_ids[i],
                u["display_name"],
                u["bio"],
                f"http://minio:9000/healthai-media/avatars/{u['username']}.jpg",
            ),
        )
    print(f"  ✔ {len(USERS)} profils insérés/ignorés")

    print("\n── Insertion des posts (30) ──────────────────────────")
    post_ids = []
    media_pool = MINIO_MEDIA_URLS[:]
    for i, content in enumerate(POST_CONTENTS):
        pid = str(uuid.uuid4())
        author = user_ids[i % len(user_ids)]
        # Distribue les 20 médias sur les 20 premiers posts
        media = [media_pool[i]] if i < len(media_pool) else []
        created = now_offset(days=random.randint(0, 30), hours=random.randint(0, 23))
        cur.execute(
            """
            INSERT INTO posts (id, user_id, content, media_urls, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            RETURNING id
            """,
            (pid, author, content, media, created),
        )
        row = cur.fetchone()
        if row:
            post_ids.append(str(row[0]))
    print(f"  ✔ {len(post_ids)} posts insérés")

    print("\n── Insertion des likes (croisés) ─────────────────────")
    likes_inserted = 0
    for post_id in post_ids:
        likers = random.sample(user_ids, k=random.randint(1, min(5, len(user_ids))))
        for liker_id in likers:
            cur.execute(
                """
                INSERT INTO likes (post_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (post_id, user_id) DO NOTHING
                """,
                (post_id, liker_id),
            )
            likes_inserted += cur.rowcount
    print(f"  ✔ {likes_inserted} likes insérés")

    print("\n── Insertion des commentaires (croisés) ──────────────")
    comments_inserted = 0
    for post_id in post_ids:
        commenters = random.sample(user_ids, k=random.randint(1, min(3, len(user_ids))))
        for commenter_id in commenters:
            comment = random.choice(COMMENT_TEMPLATES)
            cur.execute(
                """
                INSERT INTO comments (post_id, user_id, content)
                VALUES (%s, %s, %s)
                """,
                (post_id, commenter_id, comment),
            )
            comments_inserted += 1
    print(f"  ✔ {comments_inserted} commentaires insérés")

    conn.commit()
    cur.close()
    conn.close()

    print("\n══ Seed terminé avec succès ════════════════════════════")
    print(f"   Utilisateurs : {len(user_ids)}")
    print(f"   Posts        : {len(post_ids)}")
    print(f"   Médias       : {len(MINIO_MEDIA_URLS)} URLs fictives distribuées")
    print(f"   Likes        : {likes_inserted}")
    print(f"   Commentaires : {comments_inserted}")


if __name__ == "__main__":
    run()
