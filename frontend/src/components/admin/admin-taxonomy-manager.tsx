"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  type AdminTaxonomy,
  createAdminTaxonomy,
  deleteAdminTaxonomy,
  getAdminTaxonomies,
  reorderAdminTaxonomies,
  updateAdminTaxonomy,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

type TaxonomyKind = "disciplines" | "typologies";

export function AdminTaxonomyManager({ kind, title }: { kind: TaxonomyKind; title: string }) {
  const { session } = useAdminSession();
  const [items, setItems] = useState<AdminTaxonomy[]>([]);
  const [slug, setSlug] = useState("");
  const [titleEn, setTitleEn] = useState("");
  const [titleFa, setTitleFa] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const response = await getAdminTaxonomies(kind);
        if (active) setItems(response.items);
      } catch {
        if (active) setMessage("Taxonomy data is unavailable.");
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [kind]);

  const create = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (session === null) return;
    try {
      const payload = { slug, title_en: titleEn, title_fa: titleFa };
      const item = editingId === null
        ? await createAdminTaxonomy(kind, payload, session.csrf_token)
        : await updateAdminTaxonomy(kind, editingId, payload, session.csrf_token);
      setItems((current) => editingId === null ? [...current, item] : current.map((entry) => entry.id === item.id ? item : entry));
      setSlug("");
      setTitleEn("");
      setTitleFa("");
      setEditingId(null);
      setMessage(editingId === null ? "Taxonomy entry created." : "Taxonomy entry saved.");
    } catch {
      setMessage("The entry was not created. Slugs must be unique lowercase words.");
    }
  };

  const move = async (index: number, offset: -1 | 1) => {
    if (session === null) return;
    const next = [...items];
    [next[index], next[index + offset]] = [next[index + offset], next[index]];
    try {
      const response = await reorderAdminTaxonomies(kind, next.map((item) => item.id), session.csrf_token);
      setItems(response.items);
    } catch {
      setMessage("Order was not saved. Refresh before retrying.");
    }
  };

  const remove = async (item: AdminTaxonomy) => {
    if (session === null || !window.confirm(`Delete “${item.title_en}”?`)) return;
    try {
      await deleteAdminTaxonomy(kind, item.id, session.csrf_token);
      setItems((current) => current.filter((entry) => entry.id !== item.id));
    } catch {
      setMessage("This entry is used by a project or could not be deleted.");
    }
  };

  return (
    <section className="admin-projects" aria-labelledby="taxonomy-title">
      <div className="admin-dashboard__heading"><p className="admin-eyebrow">TAXONOMY</p><h1 id="taxonomy-title">{title}</h1><p>Deletion is blocked while a project references the entry.</p></div>
      <form className="admin-editor__grid" onSubmit={create}>
        <label className="admin-editor__field"><span>Slug</span><input onChange={(event) => setSlug(event.target.value)} required value={slug} /></label>
        <label className="admin-editor__field"><span>Title / EN</span><input onChange={(event) => setTitleEn(event.target.value)} required value={titleEn} /></label>
        <label className="admin-editor__field"><span>Title / FA</span><input dir="rtl" onChange={(event) => setTitleFa(event.target.value)} required value={titleFa} /></label>
        <button className="admin-primary-link" type="submit">{editingId === null ? "Create entry" : "Save entry"}</button>
      </form>
      {message ? <p className="admin-form__message" role="alert">{message}</p> : null}
      <ol className="admin-project-list">
        {items.map((item, index) => <li className="admin-project-row" key={item.id}><div><p className="admin-project-row__eyebrow">{item.display_order + 1}</p><h2>{item.title_en}</h2><p dir="rtl">{item.title_fa}</p><code>/{item.slug}</code></div><div className="admin-project-row__actions"><button disabled={index === 0} onClick={() => void move(index, -1)} type="button">↑</button><button disabled={index === items.length - 1} onClick={() => void move(index, 1)} type="button">↓</button><button onClick={() => { setEditingId(item.id); setSlug(item.slug); setTitleEn(item.title_en); setTitleFa(item.title_fa); }} type="button">Edit</button><button className="admin-project-row__delete" onClick={() => void remove(item)} type="button">Delete</button></div></li>)}
      </ol>
    </section>
  );
}
