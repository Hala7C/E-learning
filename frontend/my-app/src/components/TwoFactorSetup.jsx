import { useState } from "react";
import api from "../api/client";

export default function TwoFactorSetup() {
  const [qrCode, setQrCode] = useState(null);
  const [otp, setOtp] = useState("");
  const [status, setStatus] = useState("idle"); // idle | qr_shown | verified
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleEnable() {
    setLoading(true);
    setError(null);
    try {
      // Adjust the response field name below to match whatever your
      // backend actually returns - commonly either a base64 PNG string
      // or a raw otpauth:// URI to render into a QR code component.
      const { data } = await api.post("/api/admin/set-two-factor-auth/");
      setQrCode(data.qr_code);
      setStatus("qr_shown");
    } catch (err) {
      setError("Couldn't start 2FA setup. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post("/api/admin/verify-two-factor-auth/", { otp });
      setStatus("verified");
    } catch (err) {
      setError("Incorrect code. Check your authenticator app and try again.");
    } finally {
      setLoading(false);
    }
  }

  if (status === "verified") {
    return (
      <div className="settings-card">
        <h2>Two-factor authentication</h2>
        <p className="success-text">✓ Two-factor authentication is enabled.</p>
      </div>
    );
  }

  return (
    <div className="settings-card">
      <h2>Two-factor authentication</h2>
      {error && <p className="error-text">{error}</p>}

      {status === "idle" && (
        <>
          <p>Add an extra layer of security using an authenticator app.</p>
          <button onClick={handleEnable} disabled={loading}>
            {loading ? "Starting setup..." : "Enable 2FA"}
          </button>
        </>
      )}

      {status === "qr_shown" && (
        <>
          <p>Scan this QR code with your authenticator app, then enter the 6-digit code below.</p>
          {qrCode && (
            <img
              src={qrCode.startsWith("data:") ? qrCode : `data:image/png;base64,${qrCode}`}
              alt="2FA QR code"
              className="qr-code"
            />
          )}
          <form onSubmit={handleVerify}>
            <label>
              Verification code
              <input
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                maxLength={6}
                inputMode="numeric"
                required
              />
            </label>
            <button type="submit" disabled={loading}>
              {loading ? "Verifying..." : "Confirm"}
            </button>
          </form>
        </>
      )}
    </div>
  );
}
