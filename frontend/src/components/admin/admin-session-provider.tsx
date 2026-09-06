"use client";

import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import {
  AdminApiError,
  type AdminSession,
  getAdminSession,
  logoutAdministrator,
} from "@/lib/admin-api";

type AdminSessionContextValue = {
  isLoading: boolean;
  logout: () => Promise<void>;
  session: AdminSession | null;
  setSession: (session: AdminSession) => void;
};

const AdminSessionContext = createContext<AdminSessionContextValue | null>(null);

export function AdminSessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AdminSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    void getAdminSession()
      .then((nextSession) => {
        if (active) setSession(nextSession);
      })
      .catch((error: unknown) => {
        if (error instanceof AdminApiError && error.status === 401) return;
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const logout = useCallback(async () => {
    if (session !== null) await logoutAdministrator(session.csrf_token);
    setSession(null);
  }, [session]);

  const value = useMemo(
    () => ({ isLoading, logout, session, setSession }),
    [isLoading, logout, session],
  );
  return <AdminSessionContext.Provider value={value}>{children}</AdminSessionContext.Provider>;
}

export function useAdminSession(): AdminSessionContextValue {
  const context = useContext(AdminSessionContext);
  if (context === null) throw new Error("AdminSessionProvider is required");
  return context;
}
