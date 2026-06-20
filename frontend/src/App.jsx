import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CommunityTrends from "./pages/CommunityTrends";
import Login from "./pages/Login";
import Register from "./pages/Register";
import RequireAuth from "./components/RequireAuth";
import { logout } from "./lib/api";
import "./styles.css";

export default function App() {
  const isLoggedIn = !!localStorage.getItem("access_token");

  return (
    <BrowserRouter>
      <nav className="app-nav">
        <Link to="/">My Dashboard</Link>
        <Link to="/community">Community Trends</Link>
        <span className="app-nav__spacer" />
        {isLoggedIn ? (
          <button className="app-nav__logout" onClick={logout}>Log out</button>
        ) : (
          <Link to="/login">Log in</Link>
        )}
      </nav>
      <main>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <Dashboard />
              </RequireAuth>
            }
          />
          {/* Community trends is anonymized and public — no login required */}
          <Route path="/community" element={<CommunityTrends />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
