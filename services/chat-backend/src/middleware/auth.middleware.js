/**
 * auth.middleware.js — Authentification duale
 *
 * Priorité : HS256 (secret partagé HealthAI) → fallback RS256 Keycloak
 *
 * Variables d'env à ajouter dans le docker-compose / .env du backend :
 *   JWT_SECRET=<même secret que l'API HealthAI port 8000>
 *   KEYCLOAK_SERVER_URL=http://keycloak:8080   (inchangé)
 *   KEYCLOAK_REALM=social-network              (inchangé)
 */

const jwt    = require('jsonwebtoken');
const jwksRsa = require('jwks-rsa');
require('dotenv').config();

const KEYCLOAK_SERVER_URL = process.env.KEYCLOAK_SERVER_URL || 'http://keycloak:8080';
const REALM               = process.env.KEYCLOAK_REALM       || 'social-network';

// ── Keycloak JWKS client (RS256) ─────────────────────────────────────────────
const jwksClient = jwksRsa({
  jwksUri: `${KEYCLOAK_SERVER_URL}/realms/${REALM}/protocol/openid-connect/certs`,
  cache: true,
  rateLimit: true,
  jwksRequestsPerMinute: 10,
  timeout: 30000,
});

function getKey(header, callback) {
  jwksClient.getSigningKey(header.kid, (err, key) => {
    if (err) return callback(err);
    callback(null, key.getPublicKey() || key.rsaPublicKey);
  });
}

// ── Shared secret (HealthAI HS256) ───────────────────────────────────────────
const HS256_SECRET = process.env.JWT_SECRET || 'dev_secret_change_in_prod';

/**
 * Extract a normalized user object from any verified decoded JWT.
 * Handles both HealthAI payload shape and Keycloak payload shape.
 */
function normalizeUser(decoded) {
  return {
    // HealthAI tokens use `id` or `user_id`; Keycloak uses `sub`
    keycloakId: String(decoded.id || decoded.user_id || decoded.sub || 'unknown'),
    username:
      decoded.username ||
      decoded.preferred_username ||
      decoded.name ||
      decoded.email?.split('@')[0] ||
      'Utilisateur',
    email: decoded.email || '',
    roles: decoded.realm_access?.roles || decoded.roles || [],
  };
}

/**
 * verifyToken(req, res, next)
 *
 * 1. Try HS256 with JWT_SECRET (HealthAI tokens)
 * 2. Fallback: RS256 via Keycloak JWKS
 */
function verifyToken(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Non authentifié. Token manquant.' });
  }
  const token = authHeader.split(' ')[1];

  // ── Attempt 1 : HS256 (HealthAI) ─────────────────────────────────────────
  jwt.verify(token, HS256_SECRET, { algorithms: ['HS256'] }, (err, decoded) => {
    if (!err && decoded) {
      req.user = normalizeUser(decoded);
      return next();
    }

    // ── Attempt 2 : RS256 via Keycloak JWKS ──────────────────────────────
    jwt.verify(token, getKey, {}, (err2, decoded2) => {
      if (err2) {
        return res.status(401).json({ message: 'Session expirée ou token invalide.' });
      }
      req.user = normalizeUser(decoded2);
      next();
    });
  });
}

/**
 * getSocketKey — reused by server.js for socket.io RS256 fallback
 */
function getSocketKey(header, callback) {
  jwksClient.getSigningKey(header.kid, (err, key) => {
    if (err) return callback(err);
    callback(null, key.getPublicKey() || key.rsaPublicKey);
  });
}

module.exports = { verifyToken, getKey, getSocketKey, normalizeUser, HS256_SECRET };
