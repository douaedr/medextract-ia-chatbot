import axios from "axios";

// Toutes les requetes passent par l'API Gateway via /api (proxy nginx/vite)
const api = axios.create({ baseURL: "" });

// Injecte automatiquement le token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Redirige vers /login si le token est invalide/expire
api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401 && !location.pathname.includes("/login")) {
      localStorage.removeItem("token");
      location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
