import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/dashboard", label: "Tableau de bord" },
  { to: "/documents", label: "Documents" },
  { to: "/analyses", label: "Analyses" },
  { to: "/chat", label: "Assistant" },
  { to: "/profile", label: "Profil" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const nav = useNavigate();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">MedExtract AI</div>
        <nav>
          {links.map((l) => (
            <NavLink key={l.to} to={l.to}
              className={({ isActive }) => (isActive ? "active" : "")}>
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="userbox">
          <div><strong>{user?.full_name || user?.username}</strong></div>
          <div style={{ opacity: .7 }}>{user?.role}</div>
          <button className="logout" onClick={() => { logout(); nav("/login"); }}>
            Deconnexion
          </button>
        </div>
      </aside>
      <main className="main"><Outlet /></main>
    </div>
  );
}
