-- Migration V2 : table meal_analyses
-- Stockage des analyses nutritionnelles par photo de repas (Vision AI)

CREATE TABLE IF NOT EXISTS meal_analyses (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID            NULL REFERENCES users(id) ON DELETE SET NULL,
    image_filename      VARCHAR(255)    NOT NULL,
    vision_source       VARCHAR(50)     NOT NULL,           -- huggingface | google_vision | fallback_manual
    detected_foods      JSON            NOT NULL DEFAULT '[]',
    calories_estimated  FLOAT           NULL,
    proteins_g          FLOAT           NULL,
    carbs_g             FLOAT           NULL,
    fats_g              FLOAT           NULL,
    nutritional_balance VARCHAR(50)     NOT NULL DEFAULT 'unknown',
    recommendations     JSON            NOT NULL DEFAULT '[]',
    confidence_score    FLOAT           NOT NULL DEFAULT 0.0,
    is_fallback         BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_meal_analyses_user_id    ON meal_analyses (user_id);
CREATE INDEX IF NOT EXISTS idx_meal_analyses_created_at ON meal_analyses (created_at DESC);
