import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ email: "", username: "", password: "", full_name: "", role: "PATIENT" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k: string, v: string) => setF({ ...f, [k]: v });

  const validate = () => {
    if (!f.email.includes("@")) return "Email invalide";
    if (f.username.length < 3) return "Nom d'utilisateur trop court (min 3)";
    if (f.password.length < 6) return "Mot de passe trop court (min 6)";
    return "";
  };

  const submit = async () => {
    const v = validate();
    if (v) { setError(v); return; }
    setError(""); setLoading(true);
    try {
      await register(f);
      nav("/dashboard");
    } catch (e: any) {
      setError(e.response?.data?.detail || "Erreur lors de l'inscription");
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>Inscription</h1>
        <p className="sub">Creez votre compte patient</p>
        {error && <div className="error-box">{error}</div>}
        <div className="field"><label>Nom complet</label>
          <input value={f.full_name} onChange={(e) => set("full_name", e.target.value)} /></div>
        <div className="field"><label>Email</label>
          <input value={f.email} onChange={(e) => set("email", e.target.value)} /></div>
        <div className="field"><label>Nom d'utilisateur</label>
          <input value={f.username} onChange={(e) => set("username", e.target.value)} /></div>
        <div className="field"><label>Mot de passe</label>
          <input type="password" value={f.password} onChange={(e) => set("password", e.target.value)} /></div>
        <button style={{ width: "100%" }} onClick={submit} disabled={loading}>
          {loading ? "Creation..." : "Creer mon compte"}
        </button>
        <p className="mt muted">Deja inscrit ? <Link className="link" to="/login">Se connecter</Link></p>
      </div>
    </div>
  );
}
