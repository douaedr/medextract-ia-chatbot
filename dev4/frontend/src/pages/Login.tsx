import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, user } = useAuth();
  const nav = useNavigate();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => { if (user) nav("/dashboard"); }, [user]);

  const submit = async () => {
    setError(""); setLoading(true);
    try {
      await login(identifier, password);
      nav("/dashboard");
    } catch {
      setError("Identifiants incorrects");
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>Connexion</h1>
        <p className="sub">MedExtract AI - Plateforme d'extraction medicale</p>
        {error && <div className="error-box">{error}</div>}
        <div className="field">
          <label>Email ou nom d'utilisateur</label>
          <input value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && submit()} />
        </div>
        <div className="field">
          <label>Mot de passe</label>
          <input type="password" value={password}
                 onChange={(e) => setPassword(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && submit()} />
        </div>
        <button style={{ width: "100%" }} onClick={submit} disabled={loading}>
          {loading ? "Connexion..." : "Se connecter"}
        </button>
        <p className="mt muted">
          Pas de compte ? <Link className="link" to="/register">S'inscrire</Link>
        </p>
      </div>
    </div>
  );
}
