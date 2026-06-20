import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const logout = () => {
  localStorage.removeItem("access_token");
  window.location.href = "/login";
};

export const registerUser = (data) => api.post("/auth/register", data);

export const loginUser = (email, password) => {
  // FastAPI's OAuth2PasswordRequestForm expects form-urlencoded data,
  // with the email going in the "username" field.
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  return api.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

export const logSymptom = (data) => api.post("/symptoms/", data);
export const listSymptoms = () => api.get("/symptoms/");

export const logMood = (data) => api.post("/mental-health/", data);
export const listMoodLogs = () => api.get("/mental-health/");

export const addMedication = (data) => api.post("/medications/", data);
export const listMedications = () => api.get("/medications/");
export const removeMedication = (id) => api.delete(`/medications/${id}`);

export const getHotspots = (params) => api.get("/analytics/hotspots", { params });
export const getTrends = (params) => api.get("/analytics/trends", { params });

export const listAlerts = (geohash_prefix) =>
  api.get("/alerts/", { params: { geohash_prefix } });

export default api;
