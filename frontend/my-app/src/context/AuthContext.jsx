import { createContext, useContext, useState, useEffect } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("auth_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch the current user's data once, whenever we have a token but
  // no user object yet (e.g. on a page refresh).
  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchCurrentUser();
    }
  }, [isAuthenticated]);

  function clearError() {
    setError(null);
  }

  async function register(userData) {
    // userData shape depends on your custom Djoser serializer fields -
    // at minimum: email, password, re_password. Add first_name/last_name
    // etc. here if your backend's UserCreateSerializer requires them.
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/users/", userData);
      return { success: true };
    } catch (err) {
      setError(formatDjoserError(err));
      return { success: false };
    } finally {
      setLoading(false);
    }
  }

  async function activateAccount(uid, token) {
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/users/activation/", { uid, token });
      return true;
    } catch (err) {
      setError(formatDjoserError(err));
      return false;
    } finally {
      setLoading(false);
    }
  }

  async function login(email, password) {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post("/auth/token/login/", { email, password });
      localStorage.setItem("auth_token", data.auth_token);
      setIsAuthenticated(true);
      await fetchCurrentUser();
      return true;
    } catch (err) {
      if (!err.response) {
        setError("Couldn't reach the server. Check your connection and try again.");
      } else {
        setError("Invalid email or password.");
      }
      return false;
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    try {
      await api.post("/auth/token/logout/");
    } catch {
      // Even if the server call fails (e.g. token already invalid),
      // still clear local state - the user's intent is to be logged out.
    } finally {
      localStorage.removeItem("auth_token");
      setIsAuthenticated(false);
      setUser(null);
    }
  }

  async function fetchCurrentUser() {
    try {
      const { data } = await api.get("/auth/users/me/");
      setUser(data);
    } catch {
      // If this fails, the response interceptor already handles a 401
      // by logging out - nothing extra needed here.
    }
  }

  async function requestPasswordReset(email) {
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/users/reset_password/", { email });
      return true;
    } catch (err) {
      setError(formatDjoserError(err));
      return false;
    } finally {
      setLoading(false);
    }
  }

  async function confirmPasswordReset(uid, token, newPassword) {
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/users/reset_password_confirm/", {
        uid, token, new_password: newPassword,
      });
      return true;
    } catch (err) {
      setError(formatDjoserError(err));
      return false;
    } finally {
      setLoading(false);
    }
  }

  async function loginWithGoogle() {
  // This endpoint returns JSON containing the real Google URL to
  // navigate to - it does NOT issue an HTTP redirect itself, so we
  // have to fetch it first and then move the browser there ourselves.
  setError(null);
  const redirectUri = `${window.location.origin}/google-callback`;
  try {
    const { data } = await api.get(
      `/auth/o/google-oauth2/?redirect_uri=${encodeURIComponent(redirectUri)}`
    );
    window.location.href = data.authorization_url;
  } catch (err) {
    setError("Couldn't start Google sign-in. Please try again.");
  }
}
  async function completeGoogleLogin(state, code) {
  setLoading(true);
  setError(null);
  const redirectUri = `${window.location.origin}/google-callback`;
  try {
    const { data } = await api.post(
      `/auth/o/google-oauth2/?state=${encodeURIComponent(state)}&code=${encodeURIComponent(code)}&redirect_uri=${encodeURIComponent(redirectUri)}`
    );
    console.log("Google login response:", data); // check this in devtools
localStorage.setItem("auth_token",data.access);
    setIsAuthenticated(true);
    await fetchCurrentUser();
    return true;
  } catch (err) {
    setError("Google sign-in failed. Please try again.");
    return false;
  } finally {
    setLoading(false);
  }
}
  return (
    <AuthContext.Provider
      value={{
        isAuthenticated, user, loading, error, clearError,
        register, activateAccount, login, logout, requestPasswordReset,
        confirmPasswordReset, loginWithGoogle, completeGoogleLogin,
        fetchCurrentUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Djoser returns field-level errors as { field_name: ["message"] } -
// this flattens that into one readable string instead of "[object Object]".
function formatDjoserError(err) {
  const data = err.response?.data;
  if (!data) return "Something went wrong. Please try again.";
  if (typeof data === "string") {
    return data.trim().startsWith("<") ? "Something went wrong. Please try again." : data;
  }
  return Object.values(data).flat().join(" ");
}


export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
