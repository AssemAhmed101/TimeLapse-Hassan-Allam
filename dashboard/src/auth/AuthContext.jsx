import { createContext, useContext, useEffect, useState } from "react";
import { getCurrentUser, loadStoredAuthToken, loginUser, setAuthToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = loadStoredAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }
    getCurrentUser()
      .then((data) => setUser(data.user))
      .catch(() => setAuthToken(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const data = await loginUser(email, password);
    setAuthToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    setAuthToken(null);
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
