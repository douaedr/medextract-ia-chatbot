import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user } = useAuth();
  if (!user) return null;
  return (
    <div>
      <h1 className="page-title">Profil</h1>
      <div className="card" style={{ maxWidth: 480 }}>
        <div className="field"><label>Nom complet</label>
          <input value={user.full_name || ""} disabled /></div>
        <div className="field"><label>Email</label>
          <input value={user.email} disabled /></div>
        <div className="field"><label>Nom d'utilisateur</label>
          <input value={user.username} disabled /></div>
        <div className="field"><label>Role</label>
          <input value={user.role} disabled /></div>
      </div>
    </div>
  );
}
