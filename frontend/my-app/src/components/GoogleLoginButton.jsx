// GoogleLoginButton.jsx
// Place in: src/components/GoogleLoginButton.jsx
import { useAuth } from "../contexts/AuthContext";

export default function GoogleLoginButton() {
  const { loginWithGoogle, loading, error } = useAuth();

  return (
    <div>
      <button onClick={loginWithGoogle} disabled={loading}>
        {loading ? "Redirecting to Google..." : "Continue with Google"}
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
