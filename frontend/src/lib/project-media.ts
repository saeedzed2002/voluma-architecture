import type { AdminProjectMedia } from "./admin-api";

/**
 * Keeps the editing state compatible with the API invariant: a media asset can
 * appear only once in a project's gallery and exactly one selected asset is
 * the cover. This also repairs stale browser state created before that
 * invariant was enforced server-side.
 */
export function normalizeProjectMedia(items: AdminProjectMedia[]): AdminProjectMedia[] {
  const mediaIds = new Set<string>();
  const uniqueItems = items.filter((item) => {
    if (mediaIds.has(item.media.id)) return false;
    mediaIds.add(item.media.id);
    return true;
  });

  let coverAssigned = false;
  const normalized = uniqueItems.map((item, display_order) => {
    const is_cover = item.is_cover && !coverAssigned;
    if (is_cover) coverAssigned = true;
    return { ...item, display_order, is_cover };
  });

  if (!coverAssigned && normalized.length > 0) {
    normalized[0] = { ...normalized[0], is_cover: true };
  }

  return normalized;
}
