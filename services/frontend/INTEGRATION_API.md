# 🔗 Guide Intégration Frontend → API

**Responsable:** [Frontend Développeur]  
**Date:** 30 mars 2026  
**L'API est prête!** Maintenant connectons le frontend...

---

## ✅ État Actuel

### API (Tojo) ✅ COMPLÉTÉE
- ✅ `/auth/register` - Créer compte
- ✅ `/auth/login` - Se connecter
- ✅ `/auth/profile` - Récupérer profil
- ✅ `/api/v1/users` - Lister/CRUD utilisateurs
- ✅ Swagger docs: http://localhost:8000/docs

### Frontend React ⏳ À INTÉGRER
- ✅ Existe déjà: `AuthContext.jsx`, `Login.jsx`, `Dashboard.jsx`
- ⏳ À faire: Connecter aux vrais endpoints (pas mock)

---

## 📋 Étapes d'Intégration

### 1. Mettre à jour `services/api.js`

**Fichier:** `services/frontend/src/services/api.js`

**État actuel** (MOCK):
```javascript
export const getUsers = async () => ({
  data: [{ id: 1, name: "Alice", ... }]
});
```

**À remplacer par** (RÉEL):
```javascript
import axios from 'axios';

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_URL });

// ─ Intercepteur: Ajouter JWT token à chaque requête
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── AUTHENTIFICATION
export const register = (data) =>
  api.post('/auth/register', data);

export const login = (email, password) =>
  api.post('/auth/login', { email, password });

export const getProfile = () =>
  api.get('/auth/profile');

export const updateProfile = (data) =>
  api.put('/auth/profile', data);

export const logout = () =>
  api.post('/auth/logout');

// ─── USERS (CRUD)
export const getUsers = (limit = 10, offset = 0, filters = {}) =>
  api.get('/api/v1/users', {
    params: { limit, offset, ...filters }
  });

export const getUser = (userId) =>
  api.get(`/api/v1/users/${userId}`);

export const createUser = (data) =>
  api.post('/api/v1/users', data);

export const updateUser = (userId, data) =>
  api.put(`/api/v1/users/${userId}`, data);

export const deleteUser = (userId) =>
  api.delete(`/api/v1/users/${userId}`);

// À ajouter plus tard:
// export const getNutrition = (...)
// export const getExercises = (...)
```

---

### 2. Mettre à jour `AuthContext.jsx`

**Fichier:** `services/frontend/src/contexts/AuthContext.jsx`

**État actuel (MOCK):**
```jsx
const login = async (email, password) => {
  // Mock login
  setUser({ email });
  localStorage.setItem('user', email);
};
```

**À remplacer par (RÉEL):**
```jsx
import { login as apiLogin, register as apiRegister, getProfile as apiGetProfile } from '../services/api';

const login = async (email, password) => {
  try {
    const response = await apiLogin(email, password);
    const token = response.data.access_token;
    const user = response.data.user;
    
    // Sauvegarder token
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    setUser(user);
    setIsAuthenticated(true);
    return true;
  } catch (error) {
    console.error('Login error:', error);
    setError(error.response?.data?.detail || 'Login failed');
    return false;
  }
};

const register = async (userData) => {
  try {
    const response = await apiRegister(userData);
    const token = response.data.access_token;
    const user = response.data.user;
    
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    setUser(user);
    setIsAuthenticated(true);
    return true;
  } catch (error) {
    console.error('Register error:', error);
    setError(error.response?.data?.detail || 'Registration failed');
    return false;
  }
};

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  setUser(null);
  setIsAuthenticated(false);
};

// Au mount du component: Vérifier si token valide
useEffect(() => {
  const token = localStorage.getItem('access_token');
  if (token) {
    // Vérifier si token valide en le utilisant
    apiGetProfile()
      .then(response => {
        setUser(response.data.user);
        setIsAuthenticated(true);
      })
      .catch(() => {
        // Token invalide ou expiré
        logout();
      });
  }
}, []);
```

---

### 3. Tester Login/Register

#### Via Frontend UI

1. Démarrer API:
   ```bash
   docker-compose up api
   ```

2. Démarrer Frontend:
   ```bash
   cd services/frontend
   npm install
   npm run dev
   ```

3. Aller à `http://localhost:5173`

4. Cliquer sur "Login" → Ouvrir modal

5. **REGISTER:**
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `TestPass123` (min 8 chars)
   - Age: `30`
   - Goal: `weight_loss`
   
   → Vérifier que ça redirige vers Dashboard
   → Vérifier que `localStorage` contient `access_token`

6. **LOGIN:**
   - Refresh page
   - Logout
   - Login avec `test@example.com` / `TestPass123`
   - Vérifier que ça récupère bien les données utilisateur

#### Via Swagger (vérification)

1. Aller à http://localhost:8000/docs
2. Swagger test les endpoints directement
3. Comparer résultats avec ce que le frontend reçoit

---

### 4. Autres Pages

#### Dashboard
```jsx
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  
  return (
    <div>
      <h1>Bienvenue {user?.username}!</h1>
      <p>Votre goal: {user?.goal}</p>
      <p>Plan: {user?.plan}</p>
    </div>
  );
}
```

#### Account (Profil Utilisateur)
```jsx
import { updateProfile } from '../services/api';

const handleUpdate = async (data) => {
  try {
    const response = await updateProfile(data);
    setUser(response.data.user);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  } catch (error) {
    console.error('Update failed:', error);
  }
};
```

#### Users List (Admin)
```jsx
import { getUsers, deleteUser } from '../services/api';

export default function Users() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    getUsers(limit, offset)
      .then(response => {
        setUsers(response.data.items);
        setTotal(response.data.total);
      });
  }, [limit, offset]);

  const handleDelete = async (userId) => {
    if (window.confirm('Êtes-vous sûr?')) {
      await deleteUser(userId);
      setUsers(users.filter(u => u.id !== userId));
    }
  };

  return (
    <div>
      <h2>Utilisateurs ({total})</h2>
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Goal</th>
            <th>Plan</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>{user.goal}</td>
              <td>{user.plan}</td>
              <td>
                <button onClick={() => handleDelete(user.id)}>Supprimer</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 😕 Troubleshooting

### "CORS Error"
```
Access to XMLHttpRequest at 'http://localhost:8000/auth/login' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution:**
- Vérifier que l'API est lancée (`docker-compose up api`)
- Vérifier VITE_API_URL dans l'env

### "401 Unauthorized"
```
{
  "detail": "Token inválide ou expiré"
}
```

**Solution:**
- Token expiré → Refaire login
- Token non passé → Vérifier intercepteur axios
- Token mal formaté → Vérifier `Bearer TOKEN` dans header

### "404 endpoint not found"
```
{
  "detail": "Not Found"
}
```

**Solution:**
- Vérifier URL endpoint (ex: `/auth/login` vs `/auth/log-in`)
- Vérifier API lancée
- Consulter Swagger: http://localhost:8000/docs

### "502 Bad Gateway"
- API pas lancée
- PostgreSQL pas lancée
- Database connection error → Vérifier DATABASE_URL

---

## 🧪 Test Complet E2E

**Scénario:**
1. ✅ Frontend démarre
2. ✅ Utilisateur clique "Login"
3. ✅ Form s'affiche
4. ✅ Utilisateur entre credentials
5. ✅ Api répond avec JWT token + user data
6. ✅ Token stocké dans localStorage
7. ✅ Dashboard affiche les données
8. ✅ Logout vide localStorage
9. ✅ Redirects to login si pas token

**Script de test:**
```javascript
// Dans console browser (F12)
localStorage.clear();
```

```bash
# Puis tester dans API
curl http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

Comparer les résultats.

---

## 📊 État des Pages Frontend

| Page | État | API Needed | Notes |
|------|------|-----------|-------|
| Login | ✅ Existe | `/auth/login` ✅ | Connecté |
| Register | ✅ Existe | `/auth/register` ✅ | Connecté |
| Dashboard | ✅ Existe | `/auth/profile` ✅ | À tester |
| Account | ✅ Existe | `/auth/profile`, `/auth/profile` PUT | À tester |
| Users | ✅ Existe | `/api/v1/users` ✅ | À connecter |
| Nutrition | ⏳ Vide | `/api/v1/nutrition` ⏳ | À créer |
| Exercises | ⏳ Vide | `/api/v1/exercises` ⏳ | À créer |
| DataQuality | ⏳ Stub | `/admin/data-quality` | À créer |

---

## 🎯 Prochaines Étapes Frontend

1. **Court terme (1-2h):**
   - [ ] Mettre à jour `api.js` avec vrais endpoints
   - [ ] Mettre à jour `AuthContext.jsx`
   - [ ] Tester login/register/logout
   - [ ] Pages Auth fonctionnelles

2. **Moyen terme (3-4h):**
   - [ ] Créer routers Nutrition + Exercises (API)
   - [ ] Pages Nutrition, Exercises
   - [ ] Admin Dashboard
   - [ ] Filtres et pagination

3. **Long terme (5+ h):**
   - [ ] Tests unitaires (Jest)
   - [ ] Tests E2E (Cypress)
   - [ ] Accessibilité RGAA AA
   - [ ] Optimisations performances

---

## 📚 Documentation de Référence

- **API Swagger:** http://localhost:8000/docs
- **API README:** [services/api/README.md](../api/README.md)
- **Router Pattern:** [services/api/ROUTER_PATTERN.md](../api/ROUTER_PATTERN.md)
- **Livrable Phase 1:** [services/api/LIVRABLE_PHASE1.md](../api/LIVRABLE_PHASE1.md)

---

## 💡 Tips

1. **Toujours passer le JWT token** en header:
   ```javascript
   Authorization: Bearer eyJhbGciOi...
   ```

2. **Les mots de passe** doivent être min 8 caractères

3. **Le token expire** après 24h (refaire login)

4. **Toujours vérifier Swagger** si vous avez un doute sur l'endpoint

5. **localStorage persiste** → Logout doit la nettoyer

---

**Version:** 1.0  
**Créé:** 30 mars 2026  
**Prêt à intégrer:** ✅  
