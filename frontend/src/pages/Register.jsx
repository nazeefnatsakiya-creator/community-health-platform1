import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser, loginUser } from "../lib/api";

export default function Register() {
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [sharesData, setSharesData] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      await registerUser({
        email,
        password,
        display_name: displayName,
        shares_anonymized_data: sharesData,
      });
      // Auto-login right after successful registration
      const res = await loginUser(email, password);
      localStorage.setItem("access_token", res.data.access_token);
      navigate("/");
    } catch (err) {
      setError(
        err.response?.status === 400
          ? "That email is already registered."
          : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <form onSubmit={handleSubmit} className="auth-card">
        <h1>Create your account</h1>
        {error && <p className="auth-error" role="alert">{error}</p>}

        <label>
          Name
          <input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
            autoComplete="name"
          />
        </label>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>

        <label>
          Password (min. 8 characters)
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            autoComplete="new-password"
          />
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={sharesData}
            onChange={(e) => setSharesData(e.target.checked)}
          />
          Contribute my anonymized symptom data to community trend alerts
          (your identity is never shared — only used once enough nearby
          reports exist to keep individuals unidentifiable)
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Creating account…" : "Sign up"}
        </button>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
