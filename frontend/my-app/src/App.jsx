import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import PrivateRoute from "./components/PrivateRoute";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import ActivateAccount from "./pages/ActivateAccount";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPasswordConfirm from "./pages/ResetPasswordConfirm";
import GoogleCallback from "./pages/GoogleCallback";
import Dashboard from "./pages/Dashboard";
import TrainerProfile from "./pages/TrainerProfile";
import "./styles/index.css";
import TrainerCourses from "./pages/TrainerCourses";
import CourseCycles from "./pages/CourseCycles";
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        {/* Rendered once, outside <Routes>, so navigation is consistent
            across every page instead of each page owning its own header. */}
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/activate/:uid/:token" element={<ActivateAccount />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/password-reset/:uid/:token" element={<ResetPasswordConfirm />} />
          <Route path="/google-callback" element={<GoogleCallback />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/trainer/profile"
            element={
              <PrivateRoute>
                <TrainerProfile />
              </PrivateRoute>
            }
          />
          <Route
            path="/trainer/courses"
            element={
              <PrivateRoute>
                <TrainerCourses />
              </PrivateRoute>
            }
          />
          <Route
            path="/trainer/courses/:courseId/cycles"
            element={
              <PrivateRoute>
                <CourseCycles />
              </PrivateRoute>
            }
          />
          <Route
            path="*"
            element={
              <div className="not-found">
                <h1>Page not found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <Link to="/">Back to home</Link>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
