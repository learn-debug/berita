"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { setRedirectFn } from "./auth-redirect";

interface UserInfo {
  email: string;
  role: string;
  name: string;
}

interface AuthContextValue {
  token: string | null;
  user: UserInfo | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isOwner: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  token: null,
  user: null,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
  isOwner: false,
  loading: true,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    setRedirectFn(() => router.replace("/login"));

    fetch("/api/v1/auth/verify", { credentials: "include" })
      .then((r) => r.json())
      .then((data) => {
        if (data.valid) {
          setToken("authenticated");
          setUser({ email: data.email, role: data.role, name: data.name });
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? "Login failed");
    }
    const data = await res.json();
    setToken(data.token);
    setUser({ email: data.email, role: data.role, name: data.name });
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
    setUser(null);
    router.replace("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        login,
        logout,
        isAuthenticated: !!token,
        isOwner: user?.role === "owner",
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
