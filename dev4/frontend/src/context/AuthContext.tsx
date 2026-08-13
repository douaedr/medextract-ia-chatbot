import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import api from "../api/client";

interface User {
  id: string; email: string; username: string;
  full_name?: string; role: string;
}
interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (id: string, pw: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
}

const Ctx = createContext<AuthCtx>(null!);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { setLoading(false); return; }
    api.get("/api/auth/me")
      .then((r) => setUser(r.data))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setLoading(false));
  }, []);

  const login = async (identifier: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", identifier);
    form.append("password", password);
    const r = await api.post("/api/auth/token", form);
    localStorage.setItem("token", r.data.access_token);
    setUser(r.data.user);
  };

  const register = async (data: any) => {
    await api.post("/api/auth/register", data);
    await login(data.email, data.password);
  };

  const logout = () => { localStorage.removeItem("token"); setUser(null); };

  return (
    <Ctx.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </Ctx.Provider>
  );
}
