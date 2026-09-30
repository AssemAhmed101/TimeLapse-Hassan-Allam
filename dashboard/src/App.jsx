import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";
import Layout from "./components/Layout";
import CamerasPage from "./pages/Cameras";
import DashboardPage from "./pages/Dashboard";
import LoginPage from "./pages/Login";
import SettingsPage from "./pages/Settings";
import SnapshotsPage from "./pages/Snapshots";
import TimelapsesPage from "./pages/Timelapses";
import UsersPage from "./pages/Users";

export default function App() {
  return (
    <BrowserRouter><AuthProvider><Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/cameras" element={<CamerasPage />} />
        <Route path="/snapshots" element={<SnapshotsPage />} />
        <Route path="/timelapses" element={<TimelapsesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/users" element={<UsersPage />} />
      </Route>
    </Routes></AuthProvider></BrowserRouter>
  );
}
