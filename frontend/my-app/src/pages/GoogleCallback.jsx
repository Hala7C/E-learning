import { useEffect, useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function GoogleCallback() {
  const [searchParams] = useSearchParams();
  const { completeGoogleLogin } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState("processing"); // processing | error

  useEffect(() => {
    const state = searchParams.get("state");
    const code = searchParams.get("code");

    if (!state || !code) {
      setStatus("error");
      return;
    }

    completeGoogleLogin(state, code).then((success) => {
      if (success) {
        navigate("/");
      } else {
        setStatus("error");
      }
    });
  }, [searchParams]);

  return (
    <div className="auth-page">
      <div className="auth-form">
        {status === "processing" && <p>Signing you in with Google...</p>}
        {status === "error" && (
          <>
            <h1>Sign-in failed</h1>
            <p>Something went wrong completing Google sign-in.</p>
            <Link to="/login">Back to login</Link>
          </>
        )}
      </div>
    </div>
  );
}
