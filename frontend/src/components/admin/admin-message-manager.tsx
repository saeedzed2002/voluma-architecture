"use client";

import { useEffect, useState } from "react";

import {
  type AdminContactMessage,
  deleteAdminContactMessage,
  getAdminContactMessages,
  updateAdminContactMessageState,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

const stateLabels: Record<AdminContactMessage["state"], string> = {
  archived: "Archived",
  new: "New",
  read: "Read",
};

function dateTime(value: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value),
  );
}

export function AdminMessageManager() {
  const { session } = useAdminSession();
  const [filter, setFilter] = useState<AdminContactMessage["state"] | "all">("new");
  const [items, setItems] = useState<AdminContactMessage[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    let active = true;
    void getAdminContactMessages(filter === "all" ? undefined : filter)
      .then((response) => {
        if (!active) return;
        setItems(response.items);
        setTotal(response.total);
      })
      .catch(() => {
        if (active) setMessage("Contact messages are unavailable. Refresh to try again.");
      });
    return () => {
      active = false;
    };
  }, [filter]);

  const updateState = async (item: AdminContactMessage, state: AdminContactMessage["state"]) => {
    if (session === null) return;
    try {
      const updated = await updateAdminContactMessageState(item.id, state, session.csrf_token);
      setItems((current) => current.map((entry) => (entry.id === updated.id ? updated : entry)));
      setMessage("Message state saved.");
    } catch {
      setMessage("The message state could not be saved.");
    }
  };

  const remove = async (item: AdminContactMessage) => {
    if (session === null || !window.confirm(`Permanently delete the message from ${item.email}?`)) return;
    try {
      await deleteAdminContactMessage(item.id, session.csrf_token);
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      setTotal((current) => Math.max(0, current - 1));
      setMessage("Message permanently deleted.");
    } catch {
      setMessage("The message could not be deleted.");
    }
  };

  return (
    <section className="admin-projects" aria-labelledby="messages-title">
      <div className="admin-dashboard__heading">
        <p className="admin-eyebrow">CONTACT TRIAGE</p>
        <h1 id="messages-title">Messages</h1>
        <p>Personal data is visible only to authenticated administrators. Archive or permanently delete it under the site retention policy.</p>
      </div>
      <label className="admin-editor__field admin-message-filter">
        <span>Filter by state</span>
        <select onChange={(event) => setFilter(event.target.value as typeof filter)} value={filter}>
          <option value="all">All messages</option>
          {Object.entries(stateLabels).map(([state, label]) => (
            <option key={state} value={state}>{label}</option>
          ))}
        </select>
      </label>
      <p className="admin-project-row__eyebrow">{total} message{total === 1 ? "" : "s"}</p>
      {message ? <p className="admin-form__message" role="status">{message}</p> : null}
      <ol className="admin-project-list admin-message-list">
        {items.map((item) => (
          <li className="admin-project-row" key={item.id}>
            <div>
              <p className="admin-project-row__eyebrow">{stateLabels[item.state]} · {dateTime(item.created_at)}</p>
              <h2>{item.name}</h2>
              <p>{item.email}{item.phone ? ` · ${item.phone}` : ""}</p>
              {item.company || item.project_type ? <p>{[item.company, item.project_type].filter(Boolean).join(" · ")}</p> : null}
              <p className="admin-message-list__body" dir={item.source_locale === "fa" ? "rtl" : undefined}>{item.body}</p>
            </div>
            <div className="admin-project-row__actions">
              <label>
                <span className="sr-only">Message state</span>
                <select
                  aria-label={`State for message from ${item.email}`}
                  onChange={(event) => void updateState(item, event.target.value as AdminContactMessage["state"])}
                  value={item.state}
                >
                  {Object.entries(stateLabels).map(([state, label]) => (
                    <option key={state} value={state}>{label}</option>
                  ))}
                </select>
              </label>
              <button className="admin-project-row__delete" onClick={() => void remove(item)} type="button">Delete</button>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
