"use client";

import { useEffect, useState } from "react";

import { type AdminDashboard, getAdminDashboard } from "@/lib/admin-api";

function ContentCard({ counts, label }: { counts: Record<"draft" | "published", number>; label: string }) {
  return (
    <article className="admin-card">
      <h2>{label}</h2>
      <dl>
        <div>
          <dt>Published</dt>
          <dd>{counts.published}</dd>
        </div>
        <div>
          <dt>Draft</dt>
          <dd>{counts.draft}</dd>
        </div>
      </dl>
    </article>
  );
}

function MessageCard({ counts }: { counts: AdminDashboard["messages"] }) {
  return (
    <article className="admin-card">
      <h2>Messages</h2>
      <dl>
        <div><dt>New</dt><dd>{counts.new}</dd></div>
        <div><dt>Read</dt><dd>{counts.read}</dd></div>
        <div><dt>Archived</dt><dd>{counts.archived}</dd></div>
      </dl>
    </article>
  );
}

export function AdminDashboard() {
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let active = true;
    void getAdminDashboard()
      .then((response) => {
        if (active) setDashboard(response);
      })
      .catch(() => {
        if (active) setHasError(true);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="admin-dashboard" aria-labelledby="admin-dashboard-title">
      <div className="admin-dashboard__heading">
        <p className="admin-eyebrow">CONTENT CONTROL</p>
        <h1 id="admin-dashboard-title">Overview</h1>
        <p>Publishing and editorial operations are protected by the administrator session.</p>
      </div>
      {hasError ? <p role="alert">Dashboard data is unavailable. Refresh to try again.</p> : null}
      {dashboard === null && !hasError ? <p>Loading content counts…</p> : null}
      {dashboard !== null ? (
        <div className="admin-card-grid">
          <ContentCard counts={dashboard.projects} label="Projects" />
          <ContentCard counts={dashboard.journal_articles} label="Journal articles" />
          <MessageCard counts={dashboard.messages} />
        </div>
      ) : null}
    </section>
  );
}
