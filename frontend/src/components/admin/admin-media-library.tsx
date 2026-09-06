"use client";

/* Direct derivative URLs must be requested from Nginx, not optimized through Next.js. */
/* eslint-disable @next/next/no-img-element */

import { useEffect, useRef, useState } from "react";

import {
  deleteAdminMedia,
  getAdminMedia,
  retryAdminMedia,
  updateAdminMedia,
  uploadAdminMedia,
  type AdminMediaAsset,
  type MediaAssetMetadataWrite,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

const maxUploadBytes = 50 * 1024 * 1024;

function formatBytes(value: number) {
  return `${(value / (1024 * 1024)).toFixed(value >= 10 * 1024 * 1024 ? 0 : 1)} MiB`;
}

function asMetadata(asset: AdminMediaAsset): MediaAssetMetadataWrite {
  return {
    alt_en: asset.alt_en,
    alt_fa: asset.alt_fa,
    caption_en: asset.caption_en,
    caption_fa: asset.caption_fa,
    credit: asset.credit,
  };
}

function MediaCard({
  asset,
  isBusy,
  onDelete,
  onRetry,
  onSave,
}: {
  asset: AdminMediaAsset;
  isBusy: boolean;
  onDelete: (asset: AdminMediaAsset) => void;
  onRetry: (asset: AdminMediaAsset) => void;
  onSave: (asset: AdminMediaAsset, metadata: MediaAssetMetadataWrite) => void;
}) {
  const [metadata, setMetadata] = useState(() => asMetadata(asset));

  const set = (field: keyof MediaAssetMetadataWrite, value: string) => {
    setMetadata((current) => ({ ...current, [field]: value || null }));
  };

  return (
    <article className="admin-media-card">
      <div className="admin-media-card__preview">
        {asset.preview_url ? (
          <img alt={asset.alt_en ?? "Processed media preview"} src={asset.preview_url} />
        ) : (
          <span>{asset.processing_state === "processing" ? "Processing image…" : "No preview"}</span>
        )}
      </div>
      <div className="admin-media-card__heading">
        <div>
          <strong>{asset.processing_state}</strong>
          <small>{formatBytes(asset.source_size_bytes)} · {asset.source_width} × {asset.source_height}</small>
        </div>
        <code>{asset.id}</code>
      </div>
      {asset.processing_error ? <p className="admin-form__message" role="alert">{asset.processing_error}</p> : null}
      <div className="admin-editor__grid">
        <label className="admin-editor__field"><span>Alt text / EN</span><input onChange={(event) => set("alt_en", event.target.value)} value={metadata.alt_en ?? ""} /></label>
        <label className="admin-editor__field"><span>Alt text / FA</span><input dir="rtl" onChange={(event) => set("alt_fa", event.target.value)} value={metadata.alt_fa ?? ""} /></label>
        <label className="admin-editor__field"><span>Caption / EN</span><textarea onChange={(event) => set("caption_en", event.target.value)} value={metadata.caption_en ?? ""} /></label>
        <label className="admin-editor__field"><span>Caption / FA</span><textarea dir="rtl" onChange={(event) => set("caption_fa", event.target.value)} value={metadata.caption_fa ?? ""} /></label>
        <label className="admin-editor__field"><span>Credit</span><input onChange={(event) => set("credit", event.target.value)} value={metadata.credit ?? ""} /></label>
      </div>
      <div className="admin-projects__toolbar">
        <button disabled={isBusy} onClick={() => onSave(asset, metadata)} type="button">Save metadata</button>
        {asset.processing_state === "failed" ? <button disabled={isBusy} onClick={() => onRetry(asset)} type="button">Retry processing</button> : null}
        <button disabled={isBusy} onClick={() => onDelete(asset)} type="button">Delete asset</button>
      </div>
    </article>
  );
}

export function AdminMediaLibrary() {
  const { session } = useAdminSession();
  const inputRef = useRef<HTMLInputElement>(null);
  const [assets, setAssets] = useState<AdminMediaAsset[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void getAdminMedia()
      .then((response) => {
        if (active) setAssets(response.items);
      })
      .catch(() => {
        if (active) setMessage("The media library is unavailable. Refresh to try again.");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!assets.some((asset) => asset.processing_state === "processing")) return;
    const timer = window.setInterval(() => {
      void getAdminMedia().then((response) => setAssets(response.items)).catch(() => undefined);
    }, 3000);
    return () => window.clearInterval(timer);
  }, [assets]);

  const upload = async (file: File) => {
    if (session === null) return;
    if (file.size > maxUploadBytes) {
      setMessage("The source image exceeds the 50 MiB application limit.");
      return;
    }
    setIsBusy(true);
    setMessage(null);
    try {
      const asset = await uploadAdminMedia(file, session.csrf_token);
      setAssets((current) => [asset, ...current]);
      setMessage("Upload accepted. Browser transfer is complete; image processing is now queued.");
    } catch {
      setMessage("The image was not accepted. Use a non-animated JPEG, PNG, or WebP within the stated limits.");
    } finally {
      setIsBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const save = async (asset: AdminMediaAsset, metadata: MediaAssetMetadataWrite) => {
    if (session === null) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const saved = await updateAdminMedia(asset.id, metadata, session.csrf_token);
      setAssets((current) => current.map((entry) => (entry.id === saved.id ? saved : entry)));
      setMessage("Media metadata saved.");
    } catch {
      setMessage("Media metadata was not saved.");
    } finally {
      setIsBusy(false);
    }
  };

  const retry = async (asset: AdminMediaAsset) => {
    if (session === null) return;
    setIsBusy(true);
    setMessage(null);
    try {
      const queued = await retryAdminMedia(asset.id, session.csrf_token);
      setAssets((current) => current.map((entry) => (entry.id === queued.id ? queued : entry)));
      setMessage("Processing retry has been queued.");
    } catch {
      setMessage("The media retry could not be queued.");
    } finally {
      setIsBusy(false);
    }
  };

  const remove = async (asset: AdminMediaAsset) => {
    if (session === null) return;
    setIsBusy(true);
    setMessage(null);
    try {
      await deleteAdminMedia(asset.id, session.csrf_token);
      setAssets((current) => current.filter((entry) => entry.id !== asset.id));
      setMessage("Asset deletion has been queued after its durable soft-delete.");
    } catch {
      setMessage("The asset could not be deleted. Remove any project use before deleting it.");
    } finally {
      setIsBusy(false);
    }
  };

  if (isLoading) return <p className="admin-status">Loading media library…</p>;

  return (
    <section className="admin-media" aria-labelledby="admin-media-title">
      <div className="admin-editor__heading">
        <div>
          <p className="admin-eyebrow">MEDIA LIBRARY</p>
          <h1 id="admin-media-title">Managed media</h1>
          <p>Originals are private. Only versioned public derivatives are published after successful processing.</p>
        </div>
      </div>
      <div className="admin-media__upload">
        <input accept="image/jpeg,image/png,image/webp" aria-label="Upload media source image" disabled={isBusy} onChange={(event) => {
          const file = event.target.files?.item(0);
          if (file) void upload(file);
        }} ref={inputRef} type="file" />
        <p>JPEG, PNG, or WebP only. Maximum source size: 50 MiB. Upload progress ends at server acceptance; worker processing continues separately.</p>
      </div>
      {message ? <p className="admin-form__message" role="alert">{message}</p> : null}
      <div className="admin-media__grid">
        {assets.map((asset) => <MediaCard asset={asset} isBusy={isBusy} key={`${asset.id}-${asset.updated_at}-${asset.processing_state}`} onDelete={remove} onRetry={retry} onSave={save} />)}
      </div>
    </section>
  );
}
