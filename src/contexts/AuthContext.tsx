import { createContext, useContext, useEffect, useMemo, useState, ReactNode } from "react";

export type UserRole = "admin" | "user" | "guest";

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: UserRole;
};

type AuthContextValue = {
  user: AuthUser | null;
  signIn: (user: AuthUser) => void;
  signOut: () => void;
  isAdmin: boolean;
  isUser: boolean;
  isGuest: boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const LOCAL_STORAGE_KEY = "auth:user";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (raw) {
        const parsed: AuthUser = JSON.parse(raw);
        setUser(parsed);
      }
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    try {
      if (user) {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(user));
      } else {
        localStorage.removeItem(LOCAL_STORAGE_KEY);
      }
    } catch {
      // ignore
    }
  }, [user]);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    signIn: (u: AuthUser) => setUser(u),
    signOut: () => setUser(null),
    isAdmin: user?.role === "admin",
    isUser: user?.role === "user",
    isGuest: !user || user?.role === "guest",
  }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


