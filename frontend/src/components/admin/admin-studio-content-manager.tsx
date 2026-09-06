"use client";

import { type FormEvent, useEffect, useState } from "react";

import {
  type AdminStudioContent,
  type AdminStudioContentKind,
  createAdminStudioContent,
  deleteAdminStudioContent,
  getAdminStudioContent,
  reorderAdminStudioContent,
  updateAdminStudioContent,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

type StudioForm = Record<string, string | null>;

function blankForm(kind: AdminStudioContentKind): StudioForm {
  return kind === "people"
    ? {
        biography_en: null,
        biography_fa: null,
        name: "",
        publication_state: "draft",
        role_en: "",
        role_fa: "",
      }
    : { publication_state: "draft", title_en: "", title_fa: "" };
}

function entryTitle(item: AdminStudioContent): string {
  return "name" in item ? item.name || "Untitled draft" : item.title_en || "Untitled draft";
}

export function AdminStudioContentManager({
  kind,
  title,
}: {
  kind: AdminStudioContentKind;
  title: string;
}) {
  const { session } = useAdminSession();
  const [items, setItems] = useState<AdminStudioContent[]>([]);
  const [form, setForm] = useState<StudioForm>(() => blankForm(kind));
  const [editingId, setEditingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void getAdminStudioContent(kind)
      .then((response) => {
        if (active) setItems(response.items);
      })
      .catch(() => {
        if (active) setMessage("Studio content is unavailable.");
      });
    return () => {
      active = false;
    };
  }, [kind]);

  const reset = () => {
    setEditingId(null);
    setForm(blankForm(kind));
  };
  const setValue = (field: string, value: string | null) =>
    setForm((current) => ({ ...current, [field]: value }));

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (session === null) return;
    try {
      const saved =
        editingId === null
          ? await createAdminStudioContent(kind, form, session.csrf_token)
          : await updateAdminStudioContent(kind, editingId, form, session.csrf_token);
      setItems((current) =>
        editingId === null
          ? [...current, saved]
          : current.map((item) => (item.id === saved.id ? saved : item)),
      );
      setMessage(editingId === null ? "Draft created." : "Entry saved.");
      reset();
    } catch {
      setMessage("Published entries require complete bilingual content.");
    }
  };

  const edit = (item: AdminStudioContent) => {
    setEditingId(item.id);
    setForm(
      "name" in item
        ? {
            biography_en: item.biography_en,
            biography_fa: item.biography_fa,
            name: item.name,
            publication_state: item.publication_state,
            role_en: item.role_en,
            role_fa: item.role_fa,
          }
        : {
            publication_state: item.publication_state,
            title_en: item.title_en,
            title_fa: item.title_fa,
          },
    );
    setMessage(null);
  };

  const move = async (index: number, offset: -1 | 1) => {
    if (session === null) return;
    const next = [...items];
    [next[index], next[index + offset]] = [next[index + offset], next[index]];
    try {
      const response = await reorderAdminStudioContent(
        kind,
        next.map((item) => item.id),
        session.csrf_token,
      );
      setItems(response.items);
    } catch {
      setMessage("Order was not saved. Refresh before retrying.");
    }
  };

  const remove = async (item: AdminStudioContent) => {
    if (session === null || !window.confirm(`Delete “${entryTitle(item)}”?`)) return;
    try {
      await deleteAdminStudioContent(kind, item.id, session.csrf_token);
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      if (editingId === item.id) reset();
      setMessage("Entry deleted.");
    } catch {
      setMessage("The entry could not be deleted.");
    }
  };

  return (
    <section className="admin-projects" aria-labelledby="studio-content-title">
      <div className="admin-dashboard__heading">
        <p className="admin-eyebrow">STUDIO CONTENT</p>
        <h1 id="studio-content-title">{title}</h1>
        <p>Ordered bilingual content. Portraits and award imagery attach in the media phase.</p>
      </div>
      <form className="admin-editor__grid" onSubmit={save}>
        <label className="admin-editor__field">
          <span>Publication state</span>
          <select
            onChange={(event) => setValue("publication_state", event.target.value)}
            value={form.publication_state ?? "draft"}
          >
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </label>
        {kind === "people" ? (
          <>
            <label className="admin-editor__field">
              <span>Name</span>
              <input
                onChange={(event) => setValue("name", event.target.value)}
                value={form.name ?? ""}
              />
            </label>
            <label className="admin-editor__field">
              <span>Role / EN</span>
              <input
                onChange={(event) => setValue("role_en", event.target.value)}
                value={form.role_en ?? ""}
              />
            </label>
            <label className="admin-editor__field">
              <span>Role / FA</span>
              <input
                dir="rtl"
                onChange={(event) => setValue("role_fa", event.target.value)}
                value={form.role_fa ?? ""}
              />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Biography / EN</span>
              <textarea
                onChange={(event) => setValue("biography_en", event.target.value || null)}
                value={form.biography_en ?? ""}
              />
            </label>
            <label className="admin-editor__field admin-editor__field--wide">
              <span>Biography / FA</span>
              <textarea
                dir="rtl"
                onChange={(event) => setValue("biography_fa", event.target.value || null)}
                value={form.biography_fa ?? ""}
              />
            </label>
          </>
        ) : (
          <>
            <label className="admin-editor__field">
              <span>Title / EN</span>
              <input
                onChange={(event) => setValue("title_en", event.target.value)}
                value={form.title_en ?? ""}
              />
            </label>
            <label className="admin-editor__field">
              <span>Title / FA</span>
              <input
                dir="rtl"
                onChange={(event) => setValue("title_fa", event.target.value)}
                value={form.title_fa ?? ""}
              />
            </label>
          </>
        )}
        <div className="admin-editor__actions">
          <button className="admin-primary-link" type="submit">
            {editingId === null ? "Create draft" : "Save entry"}
          </button>
          {editingId !== null ? (
            <button onClick={reset} type="button">
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
              <h2>{entryTitle(item)}</h2>
              {"name" in item ? (
                <>
                  <p>{item.role_en || "No English role yet."}</p>
                  <p dir="rtl">{item.role_fa || "نقش فارسی ثبت نشده است."}</p>
                </>
              ) : (
                <p dir="rtl">{item.title_fa || "عنوان فارسی ثبت نشده است."}</p>
              )}
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
