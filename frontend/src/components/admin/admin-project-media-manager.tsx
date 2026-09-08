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
import { normalizeProjectMedia } from "@/lib/project-media";

import { useAdminSession } from "./admin-session-provider";

function move<T>(items: T[], index: number, offset: number) {
  const next = index + offset;
  if (next < 0 || next >= items.length) return items;
  const copy = [...items];
  const [item] = copy.splice(index, 1);
  copy.splice(next, 0, item);
  return copy;
}

function gallerySnapshot(items: AdminProjectMedia[]) {
  return items
    .map((item, index) => `${index}:${item.media.id}:${item.is_cover ? "cover" : "gallery"}`)
    .join("|");
}

export function AdminProjectMediaManager({ projectId }: { projectId: string }) {
  const { session } = useAdminSession();
  const [library, setLibrary] = useState<AdminMediaAsset[]>([]);
  const [items, setItems] = useState<AdminProjectMedia[]>([]);
  const [savedSnapshot, setSavedSnapshot] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const [media, projectMedia] = await Promise.all([getAdminMedia(), getAdminProjectMedia(projectId)]);
        if (!active) return;
        const normalizedItems = normalizeProjectMedia(projectMedia.items);
        const receivedSnapshot = gallerySnapshot(projectMedia.items);
        const normalizedSnapshot = gallerySnapshot(normalizedItems);
        setLibrary(media.items);
        setItems(normalizedItems);
        setSavedSnapshot(receivedSnapshot);
        if (receivedSnapshot !== normalizedSnapshot) {
          setMessage("Duplicate gallery entries were removed locally. Save the gallery to repair this project.");
        }
      } catch {
        if (active) setMessage("Project media is unavailable. Refresh to try again.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [projectId]);

  const add = (asset: AdminMediaAsset) => {
    setItems((current) => {
      if (current.some((item) => item.media.id === asset.id)) return current;
      return [...current, { display_order: current.length, is_cover: current.length === 0, media: asset }];
    });
  };

  const save = async () => {
    if (session === null) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const normalizedItems = normalizeProjectMedia(items);
      const response = await replaceAdminProjectMedia(
        projectId,
        normalizedItems.map((item) => ({ is_cover: item.is_cover, media_id: item.media.id })),
        session.csrf_token,
      );
      const savedItems = normalizeProjectMedia(response.items);
      setItems(savedItems);
      setSavedSnapshot(gallerySnapshot(savedItems));
      setMessage("Project gallery saved. The selected cover is now available on public project pages.");
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
  const hasUnsavedChanges = !isLoading && gallerySnapshot(items) !== savedSnapshot;

  return (
    <section className="admin-project-media" aria-labelledby="project-gallery-title">
      <div className="admin-editor__heading">
        <div>
          <h2 id="project-gallery-title">Project gallery</h2>
          <p>Choose ready images, select one cover, then save the gallery. Saving project details in another tab does not save gallery selections.</p>
        </div>
        <Link href="/admin/media">Open media library</Link>
      </div>
      {message ? <p className="admin-form__message" role="alert">{message}</p> : null}
      <p className="admin-project-media__save-state" role="status">
        {isLoading ? "Loading project gallery…" : hasUnsavedChanges ? "Gallery changes are not saved yet." : "Gallery is saved."}
      </p>
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
      {!isLoading && items.length === 0 ? <p className="admin-editor__notice">No images are saved with this project yet. Add a ready library asset below.</p> : null}
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
      <div className="admin-project-media__actions">
        <button className="admin-project-media__save" disabled={isBusy || isLoading || !hasUnsavedChanges} onClick={() => void save()} type="button">
          {isBusy ? "Saving gallery…" : "Save gallery and set public cover"}
        </button>
        <p className="admin-editor__hint">The public project image changes only after this button confirms that the gallery was saved.</p>
      </div>
    </section>
  );
}
