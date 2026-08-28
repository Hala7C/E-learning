// GoogleLoginButton.jsx
// Place in: src/components/GoogleLoginButton.jsx
//
// BUG FIX: was importing "../contexts/AuthContext" (plural) - the real
// provider lives at "../context/AuthContext" (singular), so this import
// failed to resolve and the component could never actually render.
//
// NOTE: this duplicates the inline Google button already in
// pages/Login.jsx. Recommend picking one source of truth - either have
// Login.jsx render <GoogleLoginButton /> instead of its own inline
// button, or delete this file. Left both in place since removing either
// is a product decision, not a bug fix.
import { useAuth } from "../context/AuthContext";

export default function GoogleLoginButton() {
  const { loginWithGoogle, loading, error } = useAuth();

  return (
    <div>
      <button type="button" className="google-button" onClick={loginWithGoogle} disabled={loading}>
        {loading ? "Redirecting to Google..." : "Continue with Google"}
      </button>
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
