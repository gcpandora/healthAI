/**
 * Script de seed : synchronise les comptes Keycloak (testuser, admin)
 * déjà créés par realm-export.json vers la table Postgres `users`.
 *
 * À lancer une fois que `docker compose up` est démarré et que
 * Keycloak + le backend sont prêts (healthy).
 *
 * Usage (depuis le dossier backend, en local) :
 *   node src/seed.js
 *
 * Ou directement dans le conteneur backend déjà lancé :
 *   docker compose exec backend node src/seed.js
 */
const axios = require('axios');
require('dotenv').config();

const { sequelize, User } = require('./models');

const KEYCLOAK_SERVER_URL = process.env.KEYCLOAK_SERVER_URL || 'http://keycloak:8080';
const REALM        = process.env.KEYCLOAK_REALM        || 'social-network';
const CLIENT_ID     = process.env.KEYCLOAK_CLIENT_ID     || 'social-net-back';
const CLIENT_SECRET = process.env.KEYCLOAK_CLIENT_SECRET || 'backend-client-secret-12345';

// Comptes attendus dans keycloak/realm-export.json
const SEED_USERS = [
  { username: 'testuser', email: 'testuser@example.com' },
  { username: 'admin',    email: 'admin@example.com' }
];

async function getAdminToken() {
  const params = new URLSearchParams();
  params.append('grant_type', 'client_credentials');
  params.append('client_id', CLIENT_ID);
  params.append('client_secret', CLIENT_SECRET);

  const response = await axios.post(
    `${KEYCLOAK_SERVER_URL}/realms/${REALM}/protocol/openid-connect/token`,
    params,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  return response.data.access_token;
}

async function findKeycloakUserByUsername(token, username) {
  const response = await axios.get(
    `${KEYCLOAK_SERVER_URL}/admin/realms/${REALM}/users`,
    {
      headers: { Authorization: `Bearer ${token}` },
      params: { username, exact: true }
    }
  );
  return response.data[0] || null;
}

async function run() {
  console.log('[seed] Connecting to Postgres...');
  await sequelize.authenticate();

  console.log('[seed] Authenticating against Keycloak...');
  const token = await getAdminToken();

  for (const { username, email } of SEED_USERS) {
    const kcUser = await findKeycloakUserByUsername(token, username);
    if (!kcUser) {
      console.warn(`[seed] "${username}" not found in Keycloak — did the realm import run? Skipping.`);
      continue;
    }

    const [user, created] = await User.findOrCreate({
      where: { keycloakId: kcUser.id },
      defaults: { username, email, keycloakId: kcUser.id }
    });

    if (!created) {
      // Garde la table Postgres alignée si le username/email a changé côté Keycloak
      user.username = username;
      user.email    = email;
      await user.save();
      console.log(`[seed] "${username}" already existed in Postgres (id=${user.id}) — updated.`);
    } else {
      console.log(`[seed] Created Postgres user "${username}" (id=${user.id}, keycloakId=${kcUser.id}).`);
    }
  }

  console.log('[seed] Done.');
  await sequelize.close();
}

run().catch((err) => {
  console.error('[seed] Failed:', err.response ? err.response.data : err.message);
  process.exit(1);
});
