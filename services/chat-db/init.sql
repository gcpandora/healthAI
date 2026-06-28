-- Ce script est exécuté UNE SEULE FOIS par Postgres, automatiquement,
-- au tout premier démarrage du conteneur (volume pgdata vide).
-- Il tourne dans la base par défaut définie par POSTGRES_DB (ici "postgres").
--
-- IMPORTANT : CREATE DATABASE ne peut pas être exécuté à l'intérieur
-- d'un bloc transactionnel (DO $$ ... $$, BEGIN/COMMIT, etc.) en PostgreSQL.
-- Comme ce script ne tourne que sur un volume neuf, on n'a pas besoin
-- de "IF NOT EXISTS" : on crée directement les deux bases nécessaires.

CREATE DATABASE social_place;
CREATE DATABASE keycloak;
