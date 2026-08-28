import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [form, setForm] = useState({
    email: "", password: "", re_password: "", first_name: "", last_name: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const { register, loading, error, clearError } = useAuth();
  const navigate = useNavigate();

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();
    const { success } = await register(form);
    if (success) setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="auth-page">
        <div className="auth-form">
          <h1>Check your email</h1>
          <p>
            We've sent a verification link to <strong>{form.email}</strong>.
            Click it to activate your account before logging in.
          </p>
          <Link to="/login">Back to login</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Create account</h1>
        {error && <p className="error-text">{error}</p>}
        <label>
          Email
          <input name="email" type="email" value={form.email} onChange={handleChange} required />
        </label>
        <label>
          First name <span className="optional-tag">(optional)</span>
          <input name="first_name" value={form.first_name} onChange={handleChange} />
        </label>
        <label>
          Last name <span className="optional-tag">(optional)</span>
          <input name="last_name" value={form.last_name} onChange={handleChange} />
        </label>
        <label>
          Password
          <input
            name="password" type="password" value={form.password}
            onChange={handleChange} minLength={8} required
          />
        </label>
        <label>
          Confirm password
          <input
            name="re_password" type="password" value={form.re_password}
            onChange={handleChange} minLength={8} required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Register"}
        </button>
        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
