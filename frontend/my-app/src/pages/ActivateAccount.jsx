import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// NOTE: the :uid/:token route params here must match whatever
// DJOSER['ACTIVATION_URL'] is set to in the backend's settings.py
// (e.g. "activate/{uid}/{token}") - the activation email links to a
// URL built from that setting, so this route has to line up with it
// exactly or the link in the email will 404.
export default function ActivateAccount() {
  const { uid, token } = useParams();
  const { activateAccount } = useAuth();
  const [status, setStatus] = useState("activating"); // activating | success | error

  useEffect(() => {
    activateAccount(uid, token).then((success) => {
      setStatus(success ? "success" : "error");
    });
  }, [uid, token]);

  return (
    <div className="auth-page">
      <div className="auth-form">
        {status === "activating" && <p>Activating your account...</p>}
        {status === "success" && (
          <>
            <h1>Account activated</h1>
            <p>Your email has been verified.</p>
            <Link to="/login">Log in</Link>
          </>
        )}
        {status === "error" && (
          <>
            <h1>Activation failed</h1>
            <p>This link may have expired or already been used.</p>
            <Link to="/login">Back to login</Link>
          </>
        )}
      </div>
    </div>
  );
}
