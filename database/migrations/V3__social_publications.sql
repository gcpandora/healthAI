-- ════════════════════════════════════════════════════════════════
-- HealthAI Coach — Migration V3 : Mini-réseau social
-- Fichier  : V3__social_publications.sql
-- Moteur   : PostgreSQL 16
-- Auteure  : Hanane
--
-- Compatible avec les migrations V1 et V2 existantes.
-- Ajoute les tables nécessaires au mini-réseau social :
--   - user_profiles  : profil public (photo de profil, bio, nom d'affichage)
--   - posts          : publications texte et/ou médias
--   - likes          : réactions aux publications
--   - comments       : commentaires sur les publications
--
-- Choix techniques :
--   - UUID v4 comme PK  → cohérence avec le reste du schéma
--   - media_urls TEXT[] → tableau PostgreSQL natif (jusqu'à N médias par post)
--   - ON DELETE CASCADE → suppression en cascade pour cohérence référentielle
--   - UNIQUE sur likes  → un utilisateur ne peut liker qu'une fois par post
-- ════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- TABLE : user_profiles
-- Profil public de l'utilisateur pour le réseau social
-- Séparé de la table users pour éviter tout couplage avec les
-- données médicales/biométriques sensibles
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID        NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    display_name    VARCHAR(100) NOT NULL,
    bio             TEXT,
    -- URL de l'objet MinIO : healthai-media/profiles/<uuid>.jpg
    avatar_url      TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- Trigger updated_at (réutilise la fonction créée en V1)
CREATE TRIGGER user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ─────────────────────────────────────────────────────────────────
-- TABLE : posts
-- Publications des utilisateurs (texte + médias optionnels)
-- Les médias sont stockés dans MinIO (bucket healthai-media)
-- et référencés par leurs URLs publiques
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posts (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    content     TEXT        NOT NULL CHECK (char_length(content) BETWEEN 1 AND 2000),
    -- Tableau d'URLs MinIO : photos/vidéos associées à la publication
    media_urls  TEXT[]      NOT NULL DEFAULT '{}',

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_posts_user_id    ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);

CREATE TRIGGER posts_updated_at
    BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ─────────────────────────────────────────────────────────────────
-- TABLE : likes
-- Réactions des utilisateurs aux publications
-- Contrainte UNIQUE : un utilisateur ne peut liker qu'une seule fois
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS likes (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id     UUID        NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT likes_unique_per_user_post UNIQUE (post_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id);
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : comments
-- Commentaires sur les publications
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id     UUID        NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    content     TEXT        NOT NULL CHECK (char_length(content) BETWEEN 1 AND 500),

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comments_post_id    ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);

CREATE TRIGGER comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
