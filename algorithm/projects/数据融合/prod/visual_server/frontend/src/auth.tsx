import React, { createContext, useContext, useMemo, useState } from "react";
import { api, getToken, setToken } from "./api";

type AuthState = {
  token: string | null;
  roles: string[];
  login: (u: string, p: string) => Promise<void>;
  logout: () => void;
};

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTok] = useState<string | null>(getToken());
  const [roles, setRoles] = useState<string[]>([]);
  const value = useMemo<AuthState>(
    () => ({
      token,
      roles,
      async login(u, p) {
        const r = await api.login(u, p);
        setToken(r.access_token);
        setTok(r.access_token);
        setRoles(r.roles || []);
      },
      logout() {
        setToken(null);
        setTok(null);
        setRoles([]);
      },
    }),
    [token, roles]
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("AuthProvider missing");
  return v;
}
