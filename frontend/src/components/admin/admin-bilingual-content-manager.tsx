"use client";

import { type FormEvent, useEffect, useState } from "react";

import {
  type AdminBilingualContent,
  type AdminBilingualContentKind,
  type AdminBilingualContentWrite,
  createAdminBilingualContent,
  deleteAdminBilingualContent,
  getAdminBilingualContent,
  reorderAdminBilingualContent,
  updateAdminBilingualContent,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

const emptyDraft: AdminBilingualContentWrite = {
  publication_state: "draft",
  summary_en: "",
  summary_fa: "",
  title_en: "",
  title_fa: "",
};

export function AdminBilingualContentManager({
  description,
  kind,
  title,
}: {
  description: string;
  kind: AdminBilingualContentKind;
  title: string;
}) {
  const { session } = useAdminSession();
  const [items, setItems] = useState<AdminBilingualContent[]>([]);
  const [form, setForm] = useState<AdminBilingualContentWrite>(emptyDraft);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void getAdminBilingualContent(kind)
      .then((response) => {
        if (active) setItems(response.items);
      })
      .catch(() => {
        if (active) setMessage("Editorial content is unavailable.");
      });
    return () => {
      active = false;
    };
  }, [kind]);

  const resetForm = () => {
    setEditingId(null);
    setForm(emptyDraft);
  };

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (session === null) return;
    try {
      const saved =
        editingId === null
          ? await createAdminBilingualContent(kind, form, session.csrf_token)
          : await updateAdminBilingualContent(kind, editingId, form, session.csrf_token);
      setItems((current) =>
        editingId === null
          ? [...current, saved]
          : current.map((entry) => (entry.id === saved.id ? saved : entry)),
      );
      setMessage(editingId === null ? "Draft created." : "Entry saved.");
      resetForm();
    } catch {
      setMessage("Published entries need complete English and Persian titles and descriptions.");
    }
  };

  const move = async (index: number, offset: -1 | 1) => {
    if (session === null) return;
    const reordered = [...items];
    [reordered[index], reordered[index + offset]] = [
      reordered[index + offset],
      reordered[index],
    ];
    try {
      const response = await reorderAdminBilingualContent(
        kind,
        reordered.map((item) => item.id),
        session.csrf_token,
      );
      setItems(response.items);
    } catch {
      setMessage("Order was not saved. Refresh before retrying.");
    }
  };

  const edit = (item: AdminBilingualContent) => {
    setEditingId(item.id);
    setForm({
      publication_state: item.publication_state,
      summary_en: item.summary_en,
      summary_fa: item.summary_fa,
      title_en: item.title_en,
      title_fa: item.title_fa,
    });
    setMessage(null);
  };

  const remove = async (item: AdminBilingualContent) => {
    if (session === null || !window.confirm(`Delete “${item.title_en || "this draft"}”?`)) return;
    try {
      await deleteAdminBilingualContent(kind, item.id, session.csrf_token);
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      if (editingId === item.id) resetForm();
      setMessage("Entry deleted.");
    } catch {
      setMessage("The entry could not be deleted.");
    }
  };

  return (
    <section className="admin-projects" aria-labelledby="editorial-content-title">
      <div className="admin-dashboard__heading">
        <p className="admin-eyebrow">EDITORIAL CONTENT</p>
        <h1 id="editorial-content-title">{title}</h1>
        <p>{description}</p>
      </div>
      <form className="admin-editor__grid" onSubmit={save}>
        <label className="admin-editor__field">
          <span>Publication state</span>
          <select
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                publication_state: event.target.value as AdminBilingualContentWrite["publication_state"],
              }))
            }
            value={form.publication_state}
          >
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </label>
        <label className="admin-editor__field">
          <span>Title / EN</span>
          <input
            onChange={(event) => setForm((current) => ({ ...current, title_en: event.target.value }))}
            value={form.title_en}
          />
        </label>
        <label className="admin-editor__field">
          <span>Title / FA</span>
          <input
            dir="rtl"
            onChange={(event) => setForm((current) => ({ ...current, title_fa: event.target.value }))}
            value={form.title_fa}
          />
        </label>
        <label className="admin-editor__field admin-editor__field--wide">
          <span>Description / EN</span>
          <textarea
            onChange={(event) => setForm((current) => ({ ...current, summary_en: event.target.value }))}
            value={form.summary_en}
          />
        </label>
        <label className="admin-editor__field admin-editor__field--wide">
          <span>Description / FA</span>
          <textarea
            dir="rtl"
            onChange={(event) => setForm((current) => ({ ...current, summary_fa: event.target.value }))}
            value={form.summary_fa}
          />
        </label>
        <div className="admin-editor__actions">
          <button className="admin-primary-link" type="submit">
            {editingId === null ? "Create draft" : "Save entry"}
          </button>
          {editingId !== null ? (
            <button onClick={resetForm} type="button">
              Cancel editing
            </button>
          ) : null}
        </div>
      </form>
      {message ? (
        <p className="admin-form__message" role="alert">
          {message}
        </p>
      ) : null}
      <ol className="admin-project-list">
        {items.map((item, index) => (
          <li className="admin-project-row" key={item.id}>
            <div>
              <p className="admin-project-row__eyebrow">
                {String(item.display_order + 1).padStart(2, "0")} · {item.publication_state}
              </p>
              <h2>{item.title_en || "Untitled draft"}</h2>
              <p>{item.summary_en || "No English description yet."}</p>
              <p dir="rtl">{item.title_fa || "پیش‌نویسِ بدون عنوان"}</p>
            </div>
            <div className="admin-project-row__actions">
              <button disabled={index === 0} onClick={() => void move(index, -1)} type="button">
                ↑
              </button>
              <button
                disabled={index === items.length - 1}
                onClick={() => void move(index, 1)}
                type="button"
              >
                ↓
              </button>
              <button onClick={() => edit(item)} type="button">
                Edit
              </button>
              <button className="admin-project-row__delete" onClick={() => void remove(item)} type="button">
                Delete
              </button>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
