import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";

const baseLinks = [
  { to: "/", label: "Dashboard" },
  { to: "/cameras", label: "Cameras" },
  { to: "/snapshots", label: "Snapshots" },
  { to: "/timelapses", label: "Time-Lapses" },
  { to: "/settings", label: "Settings" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const links = user?.role === "admin" ? [...baseLinks, { to: "/users", label: "Users" }] : baseLinks;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">TL</div><div><strong>Tower Time-Lapse</strong><span>Control Center</span></div></div>
        <nav className="nav">{links.map((link) => <NavLink key={link.to} to={link.to} end={link.to === "/"} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>{link.label}</NavLink>)}</nav>
        <div className="sidebar-footer"><span>{user?.full_name || "User"}</span><small>{user?.role || "viewer"}</small><button className="button small secondary sidebar-logout" onClick={logout}>Sign out</button></div>
      </aside>
      <main className="main-content"><Outlet /></main>
    </div>
  );
}
