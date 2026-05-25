"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const AUTH_KEY = "newsagent_token";

interface AuthContextValue {
  token: string | null;
  login: (password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  token: null,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
  loading: true,
});

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem(AUTH_KEY);
    if (stored) {
      fetch(`${API_BASE}/api/v1/auth/verify?token=${encodeURIComponent(stored)}`)
        .then((r) => r.json())
        .then((data) => {
          if (data.valid) {
            setToken(stored);
          } else {
            localStorage.removeItem(AUTH_KEY);
          }
        })
        .catch(() => {
          setToken(stored);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (password: string) => {
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? "Login failed");
    }
    const data = await res.json();
    localStorage.setItem(AUTH_KEY, data.token);
    setToken(data.token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_KEY);
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
