-- ════════════════════════════════════════════════════════════════
-- HealthAI Coach — Jeu de données de démonstration
-- Fichier  : seed_demo.sql
-- Auteure  : Hanane
--
-- Script seed pour le jury : 10 utilisateurs, 30 publications,
-- 20 médias référencés, likes et commentaires représentatifs.
--
-- Prérequis : migrations V1, V2 et V3 appliquées.
-- Exécution : psql $DATABASE_URL -f seed_demo.sql
-- ════════════════════════════════════════════════════════════════

BEGIN;

-- ─────────────────────────────────────────────────────────────────
-- Nettoyage préalable (idempotent)
-- ─────────────────────────────────────────────────────────────────
DELETE FROM comments;
DELETE FROM likes;
DELETE FROM posts;
DELETE FROM user_profiles;
DELETE FROM users WHERE email LIKE '%@healthai-demo.fr';

-- ─────────────────────────────────────────────────────────────────
-- 10 utilisateurs de démonstration
-- Mot de passe hashé : "Demo1234!" (bcrypt, rounds=12)
-- ─────────────────────────────────────────────────────────────────
INSERT INTO users (id, email, username, password_hash, age, gender, height_cm, weight_kg,
                   water_intake_liters, workout_frequency, goal, fitness_level, plan)
VALUES
  ('a1000000-0000-0000-0000-000000000001', 'alice@healthai-demo.fr',   'alice_fit',    '$2b$12$demo_hash_placeholder', 28, 'female', 165.0, 60.5,  2.0, 4, 'weight_loss',    'intermediate', 'premium'),
  ('a1000000-0000-0000-0000-000000000002', 'bob@healthai-demo.fr',     'bob_runner',   '$2b$12$demo_hash_placeholder', 32, 'male',   180.0, 78.0,  2.5, 5, 'muscle_gain',    'advanced',     'premium_plus'),
  ('a1000000-0000-0000-0000-000000000003', 'clara@healthai-demo.fr',   'clara_yoga',   '$2b$12$demo_hash_placeholder', 25, 'female', 162.0, 55.0,  1.8, 3, 'general_health', 'beginner',     'free'),
  ('a1000000-0000-0000-0000-000000000004', 'david@healthai-demo.fr',   'david_lift',   '$2b$12$demo_hash_placeholder', 35, 'male',   175.0, 85.0,  3.0, 6, 'muscle_gain',    'advanced',     'premium'),
  ('a1000000-0000-0000-0000-000000000005', 'emma@healthai-demo.fr',    'emma_cycle',   '$2b$12$demo_hash_placeholder', 29, 'female', 168.0, 63.0,  2.2, 4, 'weight_loss',    'intermediate', 'premium'),
  ('a1000000-0000-0000-0000-000000000006', 'felix@healthai-demo.fr',   'felix_swim',   '$2b$12$demo_hash_placeholder', 41, 'male',   178.0, 80.0,  2.8, 3, 'maintenance',    'intermediate', 'free'),
  ('a1000000-0000-0000-0000-000000000007', 'grace@healthai-demo.fr',   'grace_pilates','$2b$12$demo_hash_placeholder', 23, 'female', 160.0, 52.0,  1.5, 2, 'sleep_improvement','beginner',   'free'),
  ('a1000000-0000-0000-0000-000000000008', 'hugo@healthai-demo.fr',    'hugo_trail',   '$2b$12$demo_hash_placeholder', 38, 'male',   182.0, 74.0,  3.5, 5, 'general_health', 'advanced',     'premium_plus'),
  ('a1000000-0000-0000-0000-000000000009', 'iris@healthai-demo.fr',    'iris_dance',   '$2b$12$demo_hash_placeholder', 26, 'female', 164.0, 57.0,  2.0, 3, 'weight_loss',    'beginner',     'premium'),
  ('a1000000-0000-0000-0000-000000000010', 'julien@healthai-demo.fr',  'julien_box',   '$2b$12$demo_hash_placeholder', 31, 'male',   176.0, 82.0,  2.3, 4, 'muscle_gain',    'intermediate', 'premium');

-- ─────────────────────────────────────────────────────────────────
-- Profils publics (réseau social)
-- avatar_url : objets MinIO dans healthai-media/profiles/
-- ─────────────────────────────────────────────────────────────────
INSERT INTO user_profiles (user_id, display_name, bio, avatar_url)
VALUES
  ('a1000000-0000-0000-0000-000000000001', 'Alice 🏃‍♀️',  'Passionnée de running et de nutrition saine.',           'http://localhost:9000/healthai-media/profiles/avatar_01.jpg'),
  ('a1000000-0000-0000-0000-000000000002', 'Bob 💪',      'Coach sportif amateur, fan de musculation.',              'http://localhost:9000/healthai-media/profiles/avatar_02.jpg'),
  ('a1000000-0000-0000-0000-000000000003', 'Clara 🧘',    'Yoga et méditation au quotidien.',                        'http://localhost:9000/healthai-media/profiles/avatar_03.jpg'),
  ('a1000000-0000-0000-0000-000000000004', 'David 🏋️',   'Powerlifter, 3 compétitions cette année.',                'http://localhost:9000/healthai-media/profiles/avatar_04.jpg'),
  ('a1000000-0000-0000-0000-000000000005', 'Emma 🚴',     'Cyclisme et diététique, en route vers mon objectif !',    'http://localhost:9000/healthai-media/profiles/avatar_05.jpg'),
  ('a1000000-0000-0000-0000-000000000006', 'Félix 🏊',    'Nageur du dimanche, fan de bien-être.',                   'http://localhost:9000/healthai-media/profiles/avatar_06.jpg'),
  ('a1000000-0000-0000-0000-000000000007', 'Grace 🩰',    'Pilates & sommeil réparateur.',                           'http://localhost:9000/healthai-media/profiles/avatar_07.jpg'),
  ('a1000000-0000-0000-0000-000000000008', 'Hugo 🏔️',    'Trail runner, 1000 km par an.',                           'http://localhost:9000/healthai-media/profiles/avatar_08.jpg'),
  ('a1000000-0000-0000-0000-000000000009', 'Iris 💃',     'Danse et cardio, bonne humeur garantie.',                 'http://localhost:9000/healthai-media/profiles/avatar_09.jpg'),
  ('a1000000-0000-0000-0000-000000000010', 'Julien 🥊',   'Boxe thai et développement personnel.',                   'http://localhost:9000/healthai-media/profiles/avatar_10.jpg');

-- ─────────────────────────────────────────────────────────────────
-- 30 publications (texte + médias pour 20 d'entre elles)
-- ─────────────────────────────────────────────────────────────────
INSERT INTO posts (id, user_id, content, media_urls, created_at)
VALUES
  -- Alice (5 posts)
  ('b1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001',
   'Premier 10 km de la saison terminé ! 🎉 Merci HealthAI pour le plan d''entraînement personnalisé.',
   ARRAY['http://localhost:9000/healthai-media/posts/post_01_a.jpg'], NOW() - INTERVAL '10 days'),

  ('b1000000-0000-0000-0000-000000000002', 'a1000000-0000-0000-0000-000000000001',
   'Repas post-effort validé par l''IA nutrition : poulet, quinoa, légumes verts 🥗',
   ARRAY['http://localhost:9000/healthai-media/posts/post_02_a.jpg'], NOW() - INTERVAL '8 days'),

  ('b1000000-0000-0000-0000-000000000003', 'a1000000-0000-0000-0000-000000000001',
   'Objectif semaine atteint : -0,5 kg, +15 min d''activité quotidienne. On continue ! 💪',
   '{}', NOW() - INTERVAL '5 days'),

  ('b1000000-0000-0000-0000-000000000004', 'a1000000-0000-0000-0000-000000000001',
   'Challenge hydratation : 2L d''eau par jour pendant 30 jours. Jour 12 ✅',
   '{}', NOW() - INTERVAL '2 days'),

  ('b1000000-0000-0000-0000-000000000005', 'a1000000-0000-0000-0000-000000000001',
   'Découverte du suivi de sommeil sur HealthAI Premium. Mes nuits s''améliorent vraiment 😴',
   ARRAY['http://localhost:9000/healthai-media/posts/post_05_a.jpg'], NOW() - INTERVAL '1 day'),

  -- Bob (4 posts)
  ('b1000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000002',
   'Séance développé couché : 120 kg x 5. Nouveau PR ! L''IA a bien ciblé ma progression 🏋️',
   ARRAY['http://localhost:9000/healthai-media/posts/post_06_b.jpg'], NOW() - INTERVAL '9 days'),

  ('b1000000-0000-0000-0000-000000000007', 'a1000000-0000-0000-0000-000000000002',
   'Plan nutritionnel IA cette semaine : 3200 kcal, ratio 40/30/30. Les résultats parlent d''eux-mêmes.',
   '{}', NOW() - INTERVAL '6 days'),

  ('b1000000-0000-0000-0000-000000000008', 'a1000000-0000-0000-0000-000000000002',
   'Comparaison avant/après 3 mois avec HealthAI. La donnée ne ment pas 📊',
   ARRAY['http://localhost:9000/healthai-media/posts/post_08_b.jpg', 'http://localhost:9000/healthai-media/posts/post_08_b2.jpg'], NOW() - INTERVAL '3 days'),

  ('b1000000-0000-0000-0000-000000000009', 'a1000000-0000-0000-0000-000000000002',
   'Conseil du jour : ne négligez pas la récupération. Mon coach IA me le rappelle à chaque fin de cycle.',
   '{}', NOW() - INTERVAL '1 day'),

  -- Clara (3 posts)
  ('b1000000-0000-0000-0000-000000000010', 'a1000000-0000-0000-0000-000000000003',
   'Première séance de yoga suivie sur HealthAI 🧘 Niveau débutant validé !',
   ARRAY['http://localhost:9000/healthai-media/posts/post_10_c.jpg'], NOW() - INTERVAL '7 days'),

  ('b1000000-0000-0000-0000-000000000011', 'a1000000-0000-0000-0000-000000000003',
   'Le journal alimentaire gratuit est déjà super utile. Je réalise que je mange trop peu de protéines.',
   '{}', NOW() - INTERVAL '4 days'),

  ('b1000000-0000-0000-0000-000000000012', 'a1000000-0000-0000-0000-000000000003',
   'Séance méditation guidée + 20 min de Yoga. Corps et esprit au top 🌿',
   '{}', NOW() - INTERVAL '1 day'),

  -- David (3 posts)
  ('b1000000-0000-0000-0000-000000000013', 'a1000000-0000-0000-0000-000000000004',
   'Compétition de powerlifting ce week-end. HealthAI a optimisé ma semaine de taper 💯',
   ARRAY['http://localhost:9000/healthai-media/posts/post_13_d.jpg'], NOW() - INTERVAL '8 days'),

  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000004',
   'Résultat : 3ème place catégorie -83 kg 🥉 L''analyse post-compétition de l''IA est très pertinente.',
   ARRAY['http://localhost:9000/healthai-media/posts/post_14_d.jpg'], NOW() - INTERVAL '5 days'),

  ('b1000000-0000-0000-0000-000000000015', 'a1000000-0000-0000-0000-000000000004',
   'Nouveau cycle de 12 semaines démarré. Objectif : +5 kg sur le total.',
   '{}', NOW() - INTERVAL '2 days'),

  -- Emma (3 posts)
  ('b1000000-0000-0000-0000-000000000016', 'a1000000-0000-0000-0000-000000000005',
   '80 km de vélo aujourd''hui ! Le suivi de fréquence cardiaque Premium+ fait vraiment la différence 🚴',
   ARRAY['http://localhost:9000/healthai-media/posts/post_16_e.jpg'], NOW() - INTERVAL '6 days'),

  ('b1000000-0000-0000-0000-000000000017', 'a1000000-0000-0000-0000-000000000005',
   'Recette validée par l''IA : smoothie protéiné banane-épinards. Délicieux et efficace 🍌',
   ARRAY['http://localhost:9000/healthai-media/posts/post_17_e.jpg'], NOW() - INTERVAL '3 days'),

  ('b1000000-0000-0000-0000-000000000018', 'a1000000-0000-0000-0000-000000000005',
   '-4 kg en 2 mois. HealthAI m''a aidée à structurer mon alimentation sans me priver.',
   '{}', NOW() - INTERVAL '1 day'),

  -- Félix (3 posts)
  ('b1000000-0000-0000-0000-000000000019', 'a1000000-0000-0000-0000-000000000006',
   '1 km de natation en 22 min. Pas mon meilleur temps mais la régularité paie 🏊',
   '{}', NOW() - INTERVAL '7 days'),

  ('b1000000-0000-0000-0000-000000000020', 'a1000000-0000-0000-0000-000000000006',
   'IMC stable depuis 3 mois. L''objectif maintenance est parfaitement calibré par l''IA.',
   '{}', NOW() - INTERVAL '4 days'),

  ('b1000000-0000-0000-0000-000000000021', 'a1000000-0000-0000-0000-000000000006',
   'Session aqua-jogging improvisée. Corps content, esprit tranquille 🌊',
   ARRAY['http://localhost:9000/healthai-media/posts/post_21_f.jpg'], NOW() - INTERVAL '1 day'),

  -- Grace (2 posts)
  ('b1000000-0000-0000-0000-000000000022', 'a1000000-0000-0000-0000-000000000007',
   'Nuit de 8h grâce aux recommandations sommeil IA. Je me sens renée ! 😌',
   '{}', NOW() - INTERVAL '5 days'),

  ('b1000000-0000-0000-0000-000000000023', 'a1000000-0000-0000-0000-000000000007',
   'Cours de Pilates + routine du soir HealthAI. La régularité c''est la clé.',
   '{}', NOW() - INTERVAL '2 days'),

  -- Hugo (3 posts)
  ('b1000000-0000-0000-0000-000000000024', 'a1000000-0000-0000-0000-000000000008',
   'Trail de 30 km en montagne ⛰️ Préparation suivie sur HealthAI depuis 6 semaines.',
   ARRAY['http://localhost:9000/healthai-media/posts/post_24_h.jpg'], NOW() - INTERVAL '9 days'),

  ('b1000000-0000-0000-0000-000000000025', 'a1000000-0000-0000-0000-000000000008',
   'Analyse post-trail : 2800 kcal dépensées, récupération estimée à 48h. Data is king 📈',
   '{}', NOW() - INTERVAL '6 days'),

  ('b1000000-0000-0000-0000-000000000026', 'a1000000-0000-0000-0000-000000000008',
   'Préparation du prochain trail 50 km. HealthAI Premium+ connecté à ma montre GPS.',
   ARRAY['http://localhost:9000/healthai-media/posts/post_26_h.jpg'], NOW() - INTERVAL '2 days'),

  -- Iris (2 posts)
  ('b1000000-0000-0000-0000-000000000027', 'a1000000-0000-0000-0000-000000000009',
   'Cours de salsa + 45 min de cardio dance. HealthAI comptabilise tout comme activité physique 💃',
   ARRAY['http://localhost:9000/healthai-media/posts/post_27_i.jpg'], NOW() - INTERVAL '4 days'),

  ('b1000000-0000-0000-0000-000000000028', 'a1000000-0000-0000-0000-000000000009',
   'Première semaine Premium : les recommandations personnalisées sont bluffantes !',
   '{}', NOW() - INTERVAL '1 day'),

  -- Julien (2 posts)
  ('b1000000-0000-0000-0000-000000000029', 'a1000000-0000-0000-0000-000000000010',
   'Entraînement boxe thaï : 3 rounds de 3 min + renforcement. L''IA ajuste mes charges automatiquement 🥊',
   ARRAY['http://localhost:9000/healthai-media/posts/post_29_j.jpg'], NOW() - INTERVAL '5 days'),

  ('b1000000-0000-0000-0000-000000000030', 'a1000000-0000-0000-0000-000000000010',
   'Bilan mensuel : -2 kg, +3 kg de muscle estimé. HealthAI m''a changé la vie.',
   '{}', NOW() - INTERVAL '1 day');


-- ─────────────────────────────────────────────────────────────────
-- Likes (représentatifs — interactions croisées entre utilisateurs)
-- ─────────────────────────────────────────────────────────────────
INSERT INTO likes (post_id, user_id)
VALUES
  -- Post d'Alice (PR running) aimé par Bob, David, Hugo
  ('b1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000002'),
  ('b1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000004'),
  ('b1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000008'),
  -- Post de Bob (PR musculation) aimé par Alice, David, Julien
  ('b1000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000001'),
  ('b1000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000004'),
  ('b1000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000010'),
  -- Post de David (podium compétition) aimé par tout le monde ou presque
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000001'),
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000002'),
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000005'),
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000008'),
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000010'),
  -- Posts de Hugo (trail) aimés par Emma, Alice, Bob
  ('b1000000-0000-0000-0000-000000000024', 'a1000000-0000-0000-0000-000000000005'),
  ('b1000000-0000-0000-0000-000000000024', 'a1000000-0000-0000-0000-000000000001'),
  ('b1000000-0000-0000-0000-000000000024', 'a1000000-0000-0000-0000-000000000002'),
  -- Post d'Emma (-4 kg) aimé par Grace, Iris, Clara
  ('b1000000-0000-0000-0000-000000000018', 'a1000000-0000-0000-0000-000000000007'),
  ('b1000000-0000-0000-0000-000000000018', 'a1000000-0000-0000-0000-000000000009'),
  ('b1000000-0000-0000-0000-000000000018', 'a1000000-0000-0000-0000-000000000003'),
  -- Posts divers
  ('b1000000-0000-0000-0000-000000000010', 'a1000000-0000-0000-0000-000000000007'),
  ('b1000000-0000-0000-0000-000000000022', 'a1000000-0000-0000-0000-000000000003'),
  ('b1000000-0000-0000-0000-000000000030', 'a1000000-0000-0000-0000-000000000002');


-- ─────────────────────────────────────────────────────────────────
-- Commentaires (interactions authentiques entre membres)
-- ─────────────────────────────────────────────────────────────────
INSERT INTO comments (post_id, user_id, content)
VALUES
  -- Sur le post running d'Alice
  ('b1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000002', 'Bravo Alice ! Le plan IA est vraiment efficace 💪'),
  ('b1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000008', 'Super perf ! C''est quoi ta prochaine course ?'),
  ('b1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000005', 'Félicitations ! On s''entraîne ensemble bientôt ? 🚴'),

  -- Sur le PR de Bob
  ('b1000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000004', '120 kg ! Respect. Quel programme tu suis ?'),
  ('b1000000-0000-0000-0000-000000000006', 'a1000000-0000-0000-0000-000000000010', 'Impressionnant Bob ! On vise quoi pour le prochain cycle ?'),

  -- Sur le podium de David
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000002', 'Félicitations champ ! 🥉 Bien mérité !'),
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000001', 'Super résultat David ! L''IA t''a bien préparé 😄'),
  ('b1000000-0000-0000-0000-000000000014', 'a1000000-0000-0000-0000-000000000008', 'Prochain objectif : la 1ère place ! 💪'),

  -- Sur le post sommeil de Grace
  ('b1000000-0000-0000-0000-000000000022', 'a1000000-0000-0000-0000-000000000003', 'Le suivi sommeil m''a aussi transformée ! Continue 🌙'),
  ('b1000000-0000-0000-0000-000000000022', 'a1000000-0000-0000-0000-000000000009', 'Trop bien ! Je vais essayer les recommandations aussi.'),

  -- Sur le trail de Hugo
  ('b1000000-0000-0000-0000-000000000024', 'a1000000-0000-0000-0000-000000000001', '30 km en montagne... chapeau Hugo ! ⛰️'),
  ('b1000000-0000-0000-0000-000000000024', 'a1000000-0000-0000-0000-000000000005', 'C''est dingue cette endurance ! Respect.'),

  -- Sur le bilan d'Emma
  ('b1000000-0000-0000-0000-000000000018', 'a1000000-0000-0000-0000-000000000007', 'Trop bien Emma ! C''est motivant pour moi aussi 🙌'),
  ('b1000000-0000-0000-0000-000000000018', 'a1000000-0000-0000-0000-000000000003', 'Quel résultat ! Tu as suivi quel plan nutritionnel ?');

COMMIT;
