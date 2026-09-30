import { useEffect, useState } from "react";
import { createUser, deleteUser, getUsers, updateUser } from "../../services/api";
import { useAuth } from "../../auth/AuthContext";

export default function UsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role: "viewer" });

  async function load() {
    try { setUsers(await getUsers()); setError(""); }
    catch (err) { setError(err?.response?.data?.detail || err?.message || "Failed to load users"); }
  }
  useEffect(() => { if (user?.role === "admin") load(); }, [user]);
  if (user?.role !== "admin") return <div className="alert">Admin permission required.</div>;

  async function submit(event) {
    event.preventDefault();
    try {
      await createUser({ ...form, is_active: true });
      setForm({ email: "", full_name: "", password: "", role: "viewer" });
      await load();
    } catch (err) { setError(err?.response?.data?.detail || err?.message || "Failed to create user"); }
  }

  async function changeRole(item, role) {
    try { await updateUser(item.id, { role }); await load(); }
    catch (err) { setError(err?.response?.data?.detail || err?.message || "Failed to update user"); }
  }

  async function remove(item) {
    if (!window.confirm(`Delete ${item.email}?`)) return;
    try { await deleteUser(item.id); await load(); }
    catch (err) { setError(err?.response?.data?.detail || err?.message || "Failed to delete user"); }
  }

  return (
    <section>
      <div className="page-header"><div><p className="eyebrow">Administration</p><h1>Users & Permissions</h1><p className="page-subtitle">Manage accounts and roles.</p></div></div>
      {error ? <div className="alert">{String(error)}</div> : null}
      <form className="user-create-form" onSubmit={submit}>
        <input type="text" placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
        <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input type="password" placeholder="Password (8+ chars)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} minLength="8" required />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="viewer">Viewer</option><option value="operator">Operator</option><option value="admin">Admin</option></select>
        <button className="button primary">Create user</button>
      </form>
      <div className="table-card user-table">
        {users.map((item) => <div className="user-row" key={item.id}><div><strong>{item.full_name}</strong><span>{item.email}</span></div><select value={item.role} onChange={(e) => changeRole(item, e.target.value)} disabled={item.id === user.id}><option value="viewer">Viewer</option><option value="operator">Operator</option><option value="admin">Admin</option></select><span>{item.is_active ? "Active" : "Disabled"}</span><button className="button small danger" onClick={() => remove(item)} disabled={item.id === user.id}>Delete</button></div>)}
      </div>
    </section>
  );
}
