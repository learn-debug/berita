"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { setRedirectFn } from "./auth-redirect";

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

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    setRedirectFn(() => router.replace("/login"));

    fetch("/api/v1/auth/verify", { credentials: "include" })
      .then((r) => r.json())
      .then((data) => {
        if (data.valid) {
          setToken("authenticated");
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const login = useCallback(async (password: string) => {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? "Login failed");
    }
    const data = await res.json();
    setToken(data.token);
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // best effort — clear state regardless
    }
    setToken(null);
    router.replace("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
