import axios from "axios";

// The backend prefixes every auth URL with a language code, e.g.
// /en/auth/... or /ar/auth/.... Keeping this in one place means
// switching language is a single function call, not a find-and-replace
// across every API call in the app.
const API_ROOT = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getLanguage() {
  return localStorage.getItem("lang") || "en";
}

export function setLanguage(lang) {
  localStorage.setItem("lang", lang);
}

const api = axios.create({ baseURL: API_ROOT,
    withCredentials: true,
 });

api.interceptors.request.use((config) => {
  const isAuthPath = config.url.startsWith("/auth/");
  const alreadyPrefixed = config.url.startsWith("/en/") || config.url.startsWith("/ar/");

  if (!isAuthPath && !alreadyPrefixed) {
    config.url = `/${getLanguage()}${config.url}`;
  }

  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }

  return config;
});

// Unlike JWT, Djoser tokens don't expire/refresh automatically - a 401
// here genuinely means "log in again", not "refresh needed".
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
