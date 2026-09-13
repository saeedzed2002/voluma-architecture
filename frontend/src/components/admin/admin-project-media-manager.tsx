"use client";

/* Direct derivative URLs must be requested from Nginx, not optimized through Next.js. */
/* eslint-disable @next/next/no-img-element */

import type { AdminMediaAsset, AdminProjectMedia } from "@/lib/admin-api";
import { normalizeProjectMedia } from "@/lib/project-media";

import { AdminMediaPicker } from "./admin-media-picker";

function move<T>(items: T[], index: number, offset: number) {
  const next = index + offset;
  if (next < 0 || next >= items.length) return items;
  const copy = [...items];
  const [item] = copy.splice(index, 1);
  copy.splice(next, 0, item);
  return copy;
}

export function projectMediaSnapshot(items: AdminProjectMedia[]) {
  return items
    .map((item, index) => `${index}:${item.media.id}:${item.is_cover ? "cover" : "gallery"}`)
    .join("|");
}

export function AdminProjectMediaManager({
  disabled,
  items,
  onChange,
  savedSnapshot,
}: {
  disabled: boolean;
  items: AdminProjectMedia[];
  onChange: (items: AdminProjectMedia[]) => void;
  savedSnapshot: string;
}) {
  const updateItems = (updater: (current: AdminProjectMedia[]) => AdminProjectMedia[]) => {
    onChange(normalizeProjectMedia(updater(items)));
  };

  const add = (asset: AdminMediaAsset) => {
    updateItems((current) => {
      if (current.some((item) => item.media.id === asset.id)) return current;
      return [
        ...current,
        { display_order: current.length, is_cover: current.length === 0, media: asset },
      ];
    });
  };

  const selected = new Set(items.map((item) => item.media.id));
  const hasUnsavedChanges = projectMediaSnapshot(items) !== savedSnapshot;

  return (
    <section className="admin-project-media" aria-labelledby="project-gallery-title">
      <div className="admin-editor__heading">
        <div>
          <h2 id="project-gallery-title">Project images</h2>
          <p>Start with the cover image, then add the remaining project images in display order.</p>
        </div>
      </div>
      <p className="admin-project-media__save-state" role="status">
        {hasUnsavedChanges
          ? "Image changes will be saved with this project."
          : "Images match the saved project."}
      </p>
      <div className="admin-project-media__items">
        {items.map((item, index) => (
          <article className="admin-project-media__item" key={item.media.id}>
            {item.media.preview_url ? (
              <img alt={item.media.alt_en ?? "Project media"} src={item.media.preview_url} />
            ) : null}
            <div>
              <strong>{item.media.alt_en}</strong>
              <p dir="rtl">{item.media.alt_fa}</p>
              <label>
                <input
                  checked={item.is_cover}
                  disabled={disabled}
                  name="project-cover"
                  onChange={() =>
                    updateItems((current) =>
                      current.map((entry) => ({
                        ...entry,
                        is_cover: entry.media.id === item.media.id,
                      })),
                    )
                  }
                  type="radio"
                />{" "}
                Main image
              </label>
            </div>
            <div className="admin-projects__toolbar">
              <button
                disabled={disabled || index === 0}
                onClick={() => updateItems((current) => move(current, index, -1))}
                type="button"
              >
                Move earlier
              </button>
              <button
                disabled={disabled || index === items.length - 1}
                onClick={() => updateItems((current) => move(current, index, 1))}
                type="button"
              >
                Move later
              </button>
              <button
                disabled={disabled}
                onClick={() =>
                  updateItems((current) =>
                    current.filter((entry) => entry.media.id !== item.media.id),
                  )
                }
                type="button"
              >
                Remove
              </button>
            </div>
          </article>
        ))}
      </div>
      {items.length === 0 ? (
        <p className="admin-editor__notice">Start by adding the main image for this project.</p>
      ) : null}
      <AdminMediaPicker
        allowUnreadySelection
        disabled={disabled}
        onSelect={add}
        selectedIds={[...selected]}
        title="Project images"
      />
    </section>
  );
}
