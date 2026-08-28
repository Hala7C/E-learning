import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Same note as ActivateAccount: these route params must match whatever
// DJOSER['PASSWORD_RESET_CONFIRM_URL'] is set to on the backend.
export default function ResetPasswordConfirm() {
  const { uid, token } = useParams();
  const [password, setPassword] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const { confirmPasswordReset, loading, error, clearError } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();
    const success = await confirmPasswordReset(uid, token, password);
    if (success) setConfirmed(true);
  }

  if (confirmed) {
    return (
      <div className="auth-page">
        <div className="auth-form">
          <h1>Password reset</h1>
          <p>Your password has been changed successfully.</p>
          <Link to="/login">Log in</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Set a new password</h1>
        {error && <p className="error-text">{error}</p>}
        <label>
          New password
          <input
            type="password" value={password}
            onChange={(e) => setPassword(e.target.value)} minLength={8} required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Set new password"}
        </button>
      </form>
    </div>
  );
}
