import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Signature element: a "session strip" - a small timetable-style list.
// This isn't decorative numbering; Cycles and LiveSessionDetails in this
// platform genuinely are scheduled, numbered sessions, so a timetable
// motif is the honest way to represent what the product does, rather
// than a generic stat-block hero.
//
// NOTE: the sample sessions/categories below are placeholder copy. Wire
// them up to real data once you have public (AllowAny) endpoints for
// them, e.g. GET /{lang}/api/trainer/course/?is_student=true and a
// public categories list - right now most trainer/course endpoints
// require an authenticated user.
const sampleSessions = [
  { time: "Mon 18:00", title: "Intro to React Hooks", trainer: "S. Malik" },
  { time: "Tue 19:30", title: "Conversational Arabic I", trainer: "H. Youssef" },
  { time: "Thu 17:00", title: "Data Structures Clinic", trainer: "R. Novak" },
];

const categories = ["Programming", "Languages", "Business", "Design", "Music"];

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home">
      <section className="home-hero">
        <div className="home-hero-copy">
          <p className="home-eyebrow">Live, not pre-recorded</p>
          <h1>Learn on a real schedule, with a real trainer.</h1>
          <p className="home-lede">
            Browse courses taught in scheduled cycles, join the live session at its start
            time, and track your progress against trainers who are actually online with you.
          </p>
          <div className="home-hero-actions">
            <Link
              to={isAuthenticated ? "/dashboard" : "/register"}
              className="button-primary"
            >
              {isAuthenticated ? "Go to your dashboard" : "Create a free account"}
            </Link>
            <Link to={isAuthenticated ? "/trainer/profile" : "/login"} className="button-secondary">
              {isAuthenticated ? "Set up trainer profile" : "Log in"}
            </Link>
          </div>
        </div>

        <div className="home-hero-panel" aria-label="Upcoming live sessions">
          <div className="session-strip-header">
            <span>This week</span>
            <span>Live sessions</span>
          </div>
          <ul className="session-strip">
            {sampleSessions.map((s) => (
              <li key={s.title}>
                <span className="session-time">{s.time}</span>
                <span className="session-title">{s.title}</span>
                <span className="session-trainer">{s.trainer}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="home-section">
        <h2>How it works</h2>
        <div className="home-steps">
          <div className="home-step">
            <span className="home-step-index">Cycle 01</span>
            <h3>Pick a course</h3>
            <p>Browse published courses by category and see the trainer's track record.</p>
          </div>
          <div className="home-step">
            <span className="home-step-index">Cycle 02</span>
            <h3>Subscribe to a cycle</h3>
            <p>Each course runs in dated cycles - pick the one whose start date works for you.</p>
          </div>
          <div className="home-step">
            <span className="home-step-index">Cycle 03</span>
            <h3>Join the live session</h3>
            <p>Get your link and password automatically once payment clears, then show up live.</p>
          </div>
        </div>
      </section>

      <section className="home-section home-categories">
        <h2>Explore by category</h2>
        <ul className="category-chip-list">
          {categories.map((c) => (
            <li key={c} className="category-chip">{c}</li>
          ))}
        </ul>
      </section>

      {!isAuthenticated && (
        <section className="home-cta">
          <h2>Ready to sit in on your first session?</h2>
          <p>It takes less than a minute to create an account.</p>
          <Link to="/register" className="button-primary">Get started</Link>
        </section>
      )}
    </div>
  );
}
