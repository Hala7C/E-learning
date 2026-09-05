import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import TwoFactorSetup from "../components/TwoFactorSetup";

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome{user?.email ? `, ${user.email}` : ""}</h1>
        <button className="link-button" onClick={logout}>Log out</button>
      </header>

      <nav className="dashboard-nav">
        <Link to="/trainer/profile">Trainer Profile</Link>
      </nav>
        <nav className="dashboard-nav">
        <Link to="/trainer/profile">Trainer Profile</Link>
        <Link to="/trainer/courses">My courses</Link>
      </nav>
      {user && (
        <div className="settings-card">
          <h2>Your account</h2>
          <p>Email: {user.email}</p>
          {/* Add more fields here once you confirm the exact shape of
              /auth/users/me/'s response for this project's CustomUser model */}
        </div>
      )}

      <TwoFactorSetup />
    </div>
  );
}
