"use client";

/* Direct derivative URLs must be requested from Nginx, not optimized through Next.js. */
/* eslint-disable @next/next/no-img-element */

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  getAdminMedia,
  getAdminProjectMedia,
  replaceAdminProjectMedia,
  type AdminMediaAsset,
  type AdminProjectMedia,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

function move<T>(items: T[], index: number, offset: number) {
  const next = index + offset;
  if (next < 0 || next >= items.length) return items;
  const copy = [...items];
  const [item] = copy.splice(index, 1);
  copy.splice(next, 0, item);
  return copy;
}

export function AdminProjectMediaManager({ projectId }: { projectId: string }) {
  const { session } = useAdminSession();
  const [library, setLibrary] = useState<AdminMediaAsset[]>([]);
  const [items, setItems] = useState<AdminProjectMedia[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const [media, projectMedia] = await Promise.all([getAdminMedia(), getAdminProjectMedia(projectId)]);
        if (!active) return;
        setLibrary(media.items);
        setItems(projectMedia.items);
      } catch {
        if (active) setMessage("Project media is unavailable. Refresh to try again.");
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [projectId]);

  const add = (asset: AdminMediaAsset) => {
    setItems((current) => [...current, { display_order: current.length, is_cover: current.length === 0, media: asset }]);
  };

  const save = async () => {
    if (session === null) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const response = await replaceAdminProjectMedia(
        projectId,
        items.map((item) => ({ is_cover: item.is_cover, media_id: item.media.id })),
        session.csrf_token,
      );
      setItems(response.items);
      setMessage("Project gallery saved.");
    } catch {
      setMessage("Project gallery was not saved. Every selected asset must be ready and have alt text in both languages.");
    } finally {
      setIsBusy(false);
    }
  };

  const selected = new Set(items.map((item) => item.media.id));
  const available = library.filter(
    (asset) => asset.processing_state === "ready" && asset.alt_en && asset.alt_fa && !selected.has(asset.id),
  );

  return (
    <section className="admin-project-media" aria-labelledby="project-gallery-title">
      <div className="admin-editor__heading">
        <div>
          <h2 id="project-gallery-title">Project gallery</h2>
          <p>Only ready assets with bilingual alt text can be associated. The selected cover becomes the public project image.</p>
        </div>
        <Link href="/admin/media">Open media library</Link>
      </div>
      {message ? <p className="admin-form__message" role="alert">{message}</p> : null}
      <div className="admin-project-media__items">
        {items.map((item, index) => (
          <article className="admin-project-media__item" key={item.media.id}>
            {item.media.preview_url ? <img alt={item.media.alt_en ?? "Project media"} src={item.media.preview_url} /> : null}
            <div>
              <strong>{item.media.alt_en}</strong>
              <p dir="rtl">{item.media.alt_fa}</p>
              <label><input checked={item.is_cover} disabled={isBusy} name="project-cover" onChange={() => setItems((current) => current.map((entry) => ({ ...entry, is_cover: entry.media.id === item.media.id })))} type="radio" /> Cover image</label>
            </div>
            <div className="admin-projects__toolbar">
              <button disabled={isBusy || index === 0} onClick={() => setItems((current) => move(current, index, -1))} type="button">Move earlier</button>
              <button disabled={isBusy || index === items.length - 1} onClick={() => setItems((current) => move(current, index, 1))} type="button">Move later</button>
              <button disabled={isBusy} onClick={() => setItems((current) => current.filter((entry) => entry.media.id !== item.media.id))} type="button">Remove</button>
            </div>
          </article>
        ))}
      </div>
      <h3>Ready library assets</h3>
      {available.length ? (
        <div className="admin-project-media__available">
          {available.map((asset) => (
            <button disabled={isBusy} key={asset.id} onClick={() => add(asset)} type="button">
              {asset.preview_url ? <img alt="" src={asset.preview_url} /> : null}
              <span>{asset.alt_en}</span>
            </button>
          ))}
        </div>
      ) : <p className="admin-editor__notice">Upload and annotate a ready image in the media library to add it here.</p>}
      <button disabled={isBusy} onClick={() => void save()} type="button">{isBusy ? "Saving…" : "Save project gallery"}</button>
    </section>
  );
}
