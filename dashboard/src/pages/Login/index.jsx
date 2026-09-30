import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="brand-mark">TL</div>
        <p className="eyebrow">Tower Time-Lapse</p>
        <h1>Sign in</h1>
        <p className="page-subtitle">Use your authorized account to access the system.</p>
        {error ? <div className="alert">{String(error)}</div> : null}
        <label><span>Email</span><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label><span>Password</span><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        <button className="button primary" disabled={submitting}>{submitting ? "Signing in..." : "Sign in"}</button>
      </form>
    </div>
  );
}
