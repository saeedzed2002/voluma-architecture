"use client";

import { type ReactNode, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAdminSession } from "./admin-session-provider";

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isLoading, logout, session } = useAdminSession();

  useEffect(() => {
    if (!isLoading && session === null) router.replace("/admin/login");
  }, [isLoading, router, session]);

  if (isLoading || session === null) {
    return <main className="admin-status">Checking administrator session…</main>;
  }

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
          <Link aria-current={pathname.startsWith("/admin/projects") ? "page" : undefined} href="/admin/projects">
            Projects
          </Link>
          <Link aria-current={pathname === "/admin/disciplines" ? "page" : undefined} href="/admin/disciplines">
            Disciplines
          </Link>
          <Link aria-current={pathname === "/admin/typologies" ? "page" : undefined} href="/admin/typologies">
            Typologies
          </Link>
          <Link aria-current={pathname === "/admin/expertise" ? "page" : undefined} href="/admin/expertise">
            Expertise
          </Link>
          <Link aria-current={pathname === "/admin/process" ? "page" : undefined} href="/admin/process">
            Process
          </Link>
          <Link aria-current={pathname === "/admin/journal" ? "page" : undefined} href="/admin/journal">
            Journal
          </Link>
          <Link aria-current={pathname === "/admin/messages" ? "page" : undefined} href="/admin/messages">
            Messages
          </Link>
          <Link aria-current={pathname === "/admin/settings" ? "page" : undefined} href="/admin/settings">
            Settings
          </Link>
          <Link aria-current={pathname === "/admin/people" ? "page" : undefined} href="/admin/people">
            People
          </Link>
          <Link aria-current={pathname === "/admin/recognition" ? "page" : undefined} href="/admin/recognition">
            Recognition
          </Link>
        </nav>
        <div className="admin-sidebar__account">
          <span>{session.administrator.email}</span>
          <button onClick={() => void logout()}>Sign out</button>
        </div>
      </aside>
      <main className="admin-main" id="main-content">
        {children}
      </main>
    </div>
  );
}
