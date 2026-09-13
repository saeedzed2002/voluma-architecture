"use client";

import { type ReactNode, useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAdminSession } from "./admin-session-provider";

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isLoading, logout, session } = useAdminSession();
  const [logoutError, setLogoutError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && session === null) router.replace("/admin/login");
  }, [isLoading, router, session]);

  if (isLoading || session === null) {
    return <main className="admin-status">Checking administrator session…</main>;
  }

  const handleLogout = async () => {
    setLogoutError(null);
    if (!(await logout())) {
      setLogoutError(
        "Sign out could not reach the API. Your session is still active; try again once the API is available.",
      );
    }
  };

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <Link aria-label="VOLUMA administrator dashboard" className="admin-wordmark" href="/admin">
          VOLUMA
        </Link>
        <nav aria-label="Administrator navigation">
          <Link aria-current={pathname === "/admin" ? "page" : undefined} href="/admin">
            Overview
          </Link>
          <div className="admin-sidebar__group">
            <p>Website</p>
            <Link href="/admin/settings#home">Home page</Link>
            <Link href="/admin/settings#studio">Studio page</Link>
            <Link
              aria-current={pathname === "/admin/settings" ? "page" : undefined}
              href="/admin/settings"
            >
              Site settings
            </Link>
            <Link
              aria-current={pathname === "/admin/expertise" ? "page" : undefined}
              href="/admin/expertise"
            >
              Expertise
            </Link>
            <Link
              aria-current={pathname === "/admin/process" ? "page" : undefined}
              href="/admin/process"
            >
              Process
            </Link>
            <Link
              aria-current={pathname === "/admin/people" ? "page" : undefined}
              href="/admin/people"
            >
              People
            </Link>
            <Link
              aria-current={pathname === "/admin/recognition" ? "page" : undefined}
              href="/admin/recognition"
            >
              Recognition
            </Link>
          </div>
          <div className="admin-sidebar__group">
            <p>Content</p>
            <Link
              aria-current={pathname.startsWith("/admin/projects") ? "page" : undefined}
              href="/admin/projects"
            >
              Projects
            </Link>
            <Link
              aria-current={pathname === "/admin/journal" ? "page" : undefined}
              href="/admin/journal"
            >
              Journal
            </Link>
          </div>
          <div className="admin-sidebar__group">
            <p>Operations</p>
            <Link
              aria-current={pathname === "/admin/messages" ? "page" : undefined}
              href="/admin/messages"
            >
              Messages
            </Link>
          </div>
          <div className="admin-sidebar__group admin-sidebar__group--advanced">
            <p>Advanced</p>
            <Link
              aria-current={pathname === "/admin/media" ? "page" : undefined}
              href="/admin/media"
            >
              Media library
            </Link>
            <Link
              aria-current={pathname === "/admin/disciplines" ? "page" : undefined}
              href="/admin/disciplines"
            >
              Disciplines
            </Link>
            <Link
              aria-current={pathname === "/admin/typologies" ? "page" : undefined}
              href="/admin/typologies"
            >
              Typologies
            </Link>
          </div>
        </nav>
        <div className="admin-sidebar__account">
          <span>{session.administrator.email}</span>
          <button onClick={() => void handleLogout()}>Sign out</button>
          {logoutError ? (
            <p className="admin-sidebar__error" role="status">
              {logoutError}
            </p>
          ) : null}
        </div>
      </aside>
      <main className="admin-main" id="main-content">
        {children}
      </main>
    </div>
  );
}
