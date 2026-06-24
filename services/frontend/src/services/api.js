import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 5000
});

// Intercepteur pour ajouter automatiquement le token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── AUTHENTIFICATION ───
export const authAPI = {
  login: (email, password) => api.post("/auth/login", { email, password }),
  register: (userData) => api.post("/auth/register", userData),
  getProfile: () => api.get("/auth/profile"),
  updateProfile: (userData) => api.put("/auth/profile", userData),
  logout: () => api.post("/auth/logout")
};

// ─── UTILISATEURS ───
export const usersAPI = {
  getUsers: (params = {}) => api.get("/api/v1/users", { params }),
  getUser: (id) => api.get(`/api/v1/users/${id}`),
  createUser: (userData) => api.post("/api/v1/users", userData),
  updateUser: (id, userData) => api.put(`/api/v1/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/api/v1/users/${id}`)
};

// ─── NUTRITION ───
export const nutritionAPI = {
  getNutritionItems: (params = {}) => api.get("/api/v1/nutrition-items", { params }),
  getNutritionItem: (id) => api.get(`/api/v1/nutrition-items/${id}`),
  createNutritionItem: (itemData) => api.post("/api/v1/nutrition-items", itemData),
  updateNutritionItem: (id, itemData) => api.put(`/api/v1/nutrition-items/${id}`, itemData),
  deleteNutritionItem: (id) => api.delete(`/api/v1/nutrition-items/${id}`),
  getFoodLogs: (userId, params = {}) => api.get(`/api/v1/users/${userId}/food-logs`, { params }),
  createFoodLog: (userId, logData) => api.post(`/api/v1/users/${userId}/food-logs`, logData),
  deleteFoodLog: (userId, logId) => api.delete(`/api/v1/users/${userId}/food-logs/${logId}`)
};

// ─── EXERCICES ───
export const exercisesAPI = {
  getExercises: (params = {}) => api.get("/api/v1/exercises/", { params }),
  getExercise: (id) => api.get(`/api/v1/exercises/${id}`),
  createExercise: (exerciseData) => api.post("/api/v1/exercises/", exerciseData),
  updateExercise: (id, exerciseData) => api.put(`/api/v1/exercises/${id}`, exerciseData),
  deleteExercise: (id) => api.delete(`/api/v1/exercises/${id}`),
  getWorkoutLogs: (userId, params = {}) => api.get(`/api/v1/users/${userId}/workout-logs`, { params }),
  createWorkoutLog: (userId, logData) => api.post(`/api/v1/users/${userId}/workout-logs`, logData),
  deleteWorkoutLog: (userId, logId) => api.delete(`/api/v1/users/${userId}/workout-logs/${logId}`)
};

// ─── FONCTIONS DE COMPATIBILITÉ ───
export const getUsers = () => usersAPI.getUsers({ limit: 1000 });
export const getExercises = () => exercisesAPI.getExercises({ limit: 1000 });
export const getFoods = () => nutritionAPI.getNutritionItems({ limit: 1000 });
export const getMetrics = () => Promise.resolve({ data: [] });

// ─── VISION IA ───
export const visionAPI = {
  analyze: (payload, config = {}) =>
    api.post("/api/v1/vision/analyze-meal", payload, { timeout: 30000, ...config }),
  getAnalysis: (analysisId) =>
    api.get(`/api/v1/vision/analyze-meal/${analysisId}`),
};

// ─── RECOMMANDATIONS FITNESS ───
export const recommendationsAPI = {
  getRecommendations: (profile, config = {}) =>
    api.post("/api/v1/recommendations", profile, { timeout: 30000, ...config }),
};

// ─── ML PRÉDICTIF (ml2 Random Forest — port 8002) ───
const mlApi = axios.create({
  baseURL: "http://localhost:8002",
  timeout: 15000,
  headers: { "x-api-key": "dev_key" },
});

export const mlAPI = {
  predictDiet:         (data) => mlApi.post("/ml/predict-diet", data),
  predictFitnessLevel: (data) => mlApi.post("/ml/predict-fitness-level", data),
};

// ─── RÉSEAU SOCIAL — Publications API (port 8003) ───────────────────────────
const postsAxios = axios.create({
  baseURL: "http://localhost:8003",
  timeout: 10000,
});

// Même JWT que l'API principale
postsAxios.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const postsAPI = {
  // ── Publications ──
  getPosts: (params = {}) =>
    postsAxios.get("/posts", { params }),
  getPost: (id) =>
    postsAxios.get(`/posts/${id}`),
  createPost: (data) =>
    postsAxios.post("/posts", data),
  deletePost: (id) =>
    postsAxios.delete(`/posts/${id}`),

  // ── Médias ──
  uploadMedia: (file) => {
    const form = new FormData();
    form.append("file", file);
    return postsAxios.post("/media/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 30000,
    });
  },

  // ── Likes ──
  likePost: (id) =>
    postsAxios.post(`/posts/${id}/like`),
  unlikePost: (id) =>
    postsAxios.delete(`/posts/${id}/like`),

  // ── Commentaires ──
  getComments: (postId, params = {}) =>
    postsAxios.get(`/posts/${postId}/comments`, { params }),
  addComment: (postId, content) =>
    postsAxios.post(`/posts/${postId}/comments`, { content }),

  // ── Profil social ──
  getSocialProfile: () =>
    postsAxios.get("/users/me/profile"),
  updateSocialProfile: (data) =>
    postsAxios.patch("/users/me/profile", data),
};

export default api;
