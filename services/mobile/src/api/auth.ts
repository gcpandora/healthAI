const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000';

export async function loginApi(username: string, password: string): Promise<string> {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    if (response.status === 401) throw new Error('Identifiants invalides');
    throw new Error('Erreur de connexion');
  }

  const data = (await response.json()) as { access_token: string };
  return data.access_token;
}

export async function registerApi(
  username: string,
  email: string,
  password: string,
): Promise<void> {
  const response = await fetch(`${BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  });

  if (!response.ok) {
    const data = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(data.detail ?? "Erreur lors de l'inscription");
  }
}
