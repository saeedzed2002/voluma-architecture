"use client";

/* Direct derivative URLs must be requested from Nginx, not optimized through Next.js. */
/* eslint-disable @next/next/no-img-element */

import { type DragEvent, useCallback, useEffect, useId, useState } from "react";

import {
  getAdminMedia,
  updateAdminMedia,
  uploadAdminMedia,
  type AdminMediaAsset,
  type MediaAssetMetadataWrite,
} from "@/lib/admin-api";

import { useAdminSession } from "./admin-session-provider";

const maxUploadBytes = 50 * 1024 * 1024;

function MediaPickerCard({
  asset,
  disabled,
  onSaveMetadata,
  onSelect,
  selected,
}: {
  asset: AdminMediaAsset;
  disabled: boolean;
  onSaveMetadata: (asset: AdminMediaAsset, metadata: MediaAssetMetadataWrite) => Promise<void>;
  onSelect: (asset: AdminMediaAsset) => void;
  selected: boolean;
}) {
  const [altEn, setAltEn] = useState(asset.alt_en ?? "");
  const [altFa, setAltFa] = useState(asset.alt_fa ?? "");
  const [captionEn, setCaptionEn] = useState(asset.caption_en ?? "");
  const [captionFa, setCaptionFa] = useState(asset.caption_fa ?? "");
  const [credit, setCredit] = useState(asset.credit ?? "");
  const [isSaving, setIsSaving] = useState(false);

  const saveMetadata = async () => {
    setIsSaving(true);
    try {
      await onSaveMetadata(asset, {
        alt_en: altEn.trim() || null,
        alt_fa: altFa.trim() || null,
        caption_en: captionEn.trim() || null,
        caption_fa: captionFa.trim() || null,
        credit: credit.trim() || null,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const canSelect = asset.processing_state === "ready" && Boolean(asset.alt_en && asset.alt_fa);

  return (
    <article className="admin-media-picker__card">
      <div className="admin-media-picker__preview">
        {asset.preview_url ? (
          <img alt={asset.alt_en ?? "Managed media preview"} src={asset.preview_url} />
        ) : (
          <span>{asset.processing_state}</span>
        )}
      </div>
      <div className="admin-media-picker__heading">
        <strong>{asset.processing_state}</strong>
        <code>{asset.id}</code>
      </div>
      {asset.processing_error ? (
        <p className="admin-form__message" role="alert">
          {asset.processing_error}
        </p>
      ) : null}
      <div className="admin-media-picker__metadata">
        <label className="admin-editor__field">
          <span>Alt text / EN</span>
          <input
            disabled={disabled || isSaving}
            onChange={(event) => setAltEn(event.target.value)}
            value={altEn}
          />
        </label>
        <label className="admin-editor__field">
          <span>Alt text / FA</span>
          <input
            dir="rtl"
            disabled={disabled || isSaving}
            onChange={(event) => setAltFa(event.target.value)}
            value={altFa}
          />
        </label>
        <label className="admin-editor__field">
          <span>Caption / EN</span>
          <input
            disabled={disabled || isSaving}
            onChange={(event) => setCaptionEn(event.target.value)}
            value={captionEn}
          />
        </label>
        <label className="admin-editor__field">
          <span>Caption / FA</span>
          <input
            dir="rtl"
            disabled={disabled || isSaving}
            onChange={(event) => setCaptionFa(event.target.value)}
            value={captionFa}
          />
        </label>
        <label className="admin-editor__field">
          <span>Credit</span>
          <input
            disabled={disabled || isSaving}
            onChange={(event) => setCredit(event.target.value)}
            value={credit}
          />
        </label>
        <button disabled={disabled || isSaving} onClick={() => void saveMetadata()} type="button">
          {isSaving ? "Saving media metadata…" : "Save media metadata"}
        </button>
      </div>
      <button
        disabled={disabled || selected || !canSelect}
        onClick={() => onSelect(asset)}
        type="button"
      >
        {selected
          ? "Selected"
          : canSelect
            ? "Select image"
            : "Processing or bilingual alt text required"}
      </button>
    </article>
  );
}

export function AdminMediaPicker({
  disabled = false,
  onAssetUpdated,
  onSelect,
  selectedIds = [],
  title = "Managed images",
}: {
  disabled?: boolean;
  onAssetUpdated?: (asset: AdminMediaAsset) => void;
  onSelect: (asset: AdminMediaAsset) => void;
  selectedIds?: string[];
  title?: string;
}) {
  const { session } = useAdminSession();
  const inputId = useId();
  const [assets, setAssets] = useState<AdminMediaAsset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const response = await getAdminMedia();
      setAssets(response.items);
    } catch {
      setMessage("Managed media is unavailable. Refresh to try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isOpen || !assets.some((asset) => asset.processing_state === "processing")) return;
    const interval = window.setInterval(() => void refresh(), 3_000);
    return () => window.clearInterval(interval);
  }, [assets, isOpen, refresh]);

  const upload = async (files: FileList | File[]) => {
    if (session === null) return;
    const selectedFiles = Array.from(files);
    if (selectedFiles.length === 0) return;
    if (selectedFiles.some((file) => file.size > maxUploadBytes)) {
      setMessage("Each image must be no larger than 50 MiB.");
      return;
    }
    setIsUploading(true);
    setMessage(null);
    try {
      const uploaded: AdminMediaAsset[] = [];
      for (const file of selectedFiles) {
        uploaded.push(await uploadAdminMedia(file, session.csrf_token));
      }
      setAssets((current) => [...uploaded, ...current]);
      uploaded.forEach((asset) => onAssetUpdated?.(asset));
      setMessage(
        uploaded.length === 1
          ? "Image accepted. Add bilingual alt text while processing continues."
          : `${uploaded.length} images accepted. Add bilingual alt text while processing continues.`,
      );
    } catch {
      setMessage(
        "An image could not be uploaded. Use a JPEG, PNG, or WebP file no larger than 50 MiB.",
      );
    } finally {
      setIsUploading(false);
    }
  };

  const saveMetadata = async (asset: AdminMediaAsset, metadata: MediaAssetMetadataWrite) => {
    if (session === null) return;
    try {
      const saved = await updateAdminMedia(asset.id, metadata, session.csrf_token);
      setAssets((current) => current.map((entry) => (entry.id === saved.id ? saved : entry)));
      onAssetUpdated?.(saved);
      setMessage("Media metadata saved.");
    } catch {
      setMessage("Media metadata was not saved.");
    }
  };

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (!disabled && !isUploading) void upload(event.dataTransfer.files);
  };

  const toggleOpen = () => {
    const nextIsOpen = !isOpen;
    setIsOpen(nextIsOpen);
    if (nextIsOpen) void refresh();
  };

  return (
    <section className="admin-media-picker" aria-label={title}>
      <div className="admin-media-picker__heading">
        <div>
          <h3>{title}</h3>
          <p>
            {selectedIds.length
              ? `${selectedIds.length} image${selectedIds.length === 1 ? "" : "s"} selected.`
              : "No image selected yet."}
          </p>
        </div>
        <button
          disabled={disabled || isUploading}
          onClick={toggleOpen}
          type="button"
        >
          {isOpen ? "Hide managed images" : "Choose or upload image"}
        </button>
      </div>
      {isOpen ? (
        <>
          <div
            className="admin-media-picker__upload"
            onDragOver={(event) => event.preventDefault()}
            onDrop={onDrop}
          >
            <input
              accept="image/jpeg,image/png,image/webp"
              disabled={disabled || isUploading}
              id={inputId}
              multiple
              onChange={(event) => {
                if (event.target.files) void upload(event.target.files);
                event.currentTarget.value = "";
              }}
              type="file"
            />
            <label htmlFor={inputId}>
              {isUploading ? "Uploading images…" : "Drop images here or choose files"}
            </label>
            <small>JPEG, PNG, or WebP — up to 50 MiB per image.</small>
          </div>
          <button
            disabled={disabled || isLoading || isUploading}
            onClick={() => void refresh()}
            type="button"
          >
            Refresh status
          </button>
          {message ? (
            <p className="admin-form__message" role="status">
              {message}
            </p>
          ) : null}
          {isLoading ? <p className="admin-editor__notice">Loading managed images…</p> : null}
          {!isLoading ? (
            <div className="admin-media-picker__grid">
              {assets.map((asset) => (
                <MediaPickerCard
                  asset={asset}
                  disabled={disabled}
                  key={`${asset.id}-${asset.updated_at}`}
                  onSaveMetadata={saveMetadata}
                  onSelect={onSelect}
                  selected={selectedIds.includes(asset.id)}
                />
              ))}
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
