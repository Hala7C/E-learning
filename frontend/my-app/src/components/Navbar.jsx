import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Single shared nav rendered once in App.jsx, outside <Routes>, so it
// persists across every page instead of each page hand-rolling its own
// header (Dashboard.jsx previously did this on its own).
export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  async function handleLogout() {
    setOpen(false);
    await logout();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand" onClick={() => setOpen(false)}>
          <span className="navbar-brand-mark" aria-hidden="true" />
          eLearning
        </Link>

        <button
          type="button"
          className="navbar-toggle"
          aria-expanded={open}
          aria-label="Toggle navigation"
          onClick={() => setOpen((v) => !v)}
        >
          <span />
          <span />
          <span />
        </button>

        <nav className={`navbar-links ${open ? "is-open" : ""}`}>
          <NavLink to="/" end onClick={() => setOpen(false)}>Home</NavLink>

          {isAuthenticated ? (
            <>
              <NavLink to="/dashboard" onClick={() => setOpen(false)}>Dashboard</NavLink>
              <NavLink to="/trainer/profile" onClick={() => setOpen(false)}>Trainer Profile</NavLink>
              <span className="navbar-user">{user?.email}</span>
              <button type="button" className="navbar-cta navbar-cta-outline" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" onClick={() => setOpen(false)}>Log in</NavLink>
              <Link to="/register" className="navbar-cta" onClick={() => setOpen(false)}>
                Get started
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
