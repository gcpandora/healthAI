const axios = require('axios');
require('dotenv').config();

const KEYCLOAK_SERVER_URL = process.env.KEYCLOAK_SERVER_URL || 'http://keycloak:8080';
const REALM = process.env.KEYCLOAK_REALM || 'social-network';
const CLIENT_ID = process.env.KEYCLOAK_CLIENT_ID || 'social-net-back';
const CLIENT_SECRET = process.env.KEYCLOAK_CLIENT_SECRET || 'backend-client-secret-12345';

async function getAdminToken() {
  try {
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
  } catch (error) {
    console.error('Keycloak Auth Error:', error.response ? error.response.data : error.message);
    throw new Error('Failed to authenticate backend with Keycloak admin.');
  }
}

async function createKeycloakUser(username, email, password) {
  try {
    const token = await getAdminToken();

    const userPayload = {
      username,
      email,
      enabled: true,
      credentials: [
        {
          type: 'password',
          value: password,
          temporary: false
        }
      ]
    };

    const response = await axios.post(
      `${KEYCLOAK_SERVER_URL}/admin/realms/${REALM}/users`,
      userPayload,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const locationHeader = response.headers.location;
    let keycloakId = '';
    if (locationHeader) {
      const parts = locationHeader.split('/');
      keycloakId = parts[parts.length - 1];
    }

    return keycloakId;
  } catch (error) {
    console.error('Keycloak User Creation Error:', error.response ? error.response.data : error.message);
    throw new Error(
      error.response && error.response.data && error.response.data.errorMessage
        ? error.response.data.errorMessage
        : 'Failed to create user in Keycloak.'
    );
  }
}

async function updateKeycloakUser(keycloakId, username, email, password) {
  if (!keycloakId) return;
  try {
    const token = await getAdminToken();

    const userPayload = {
      username,
      email
    };

    await axios.put(
      `${KEYCLOAK_SERVER_URL}/admin/realms/${REALM}/users/${keycloakId}`,
      userPayload,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (password) {
      await axios.put(
        `${KEYCLOAK_SERVER_URL}/admin/realms/${REALM}/users/${keycloakId}/reset-password`,
        {
          type: 'password',
          value: password,
          temporary: false
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
    }
  } catch (error) {
    console.error('Keycloak User Update Error:', error.response ? error.response.data : error.message);
    throw new Error('Failed to update user in Keycloak.');
  }
}

async function deleteKeycloakUser(keycloakId) {
  if (!keycloakId) return;
  try {
    const token = await getAdminToken();

    await axios.delete(
      `${KEYCLOAK_SERVER_URL}/admin/realms/${REALM}/users/${keycloakId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
  } catch (error) {
    console.error('Keycloak User Deletion Error:', error.response ? error.response.data : error.message);
    throw new Error('Failed to delete user in Keycloak.');
  }
}

module.exports = {
  createKeycloakUser,
  updateKeycloakUser,
  deleteKeycloakUser
};
