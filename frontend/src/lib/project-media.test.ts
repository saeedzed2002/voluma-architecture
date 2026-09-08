import { describe, expect, it } from "vitest";

import type { AdminProjectMedia } from "./admin-api";
import { normalizeProjectMedia } from "./project-media";

function projectMedia(id: string, is_cover = false): AdminProjectMedia {
  return {
    display_order: 99,
    is_cover,
    media: { id } as AdminProjectMedia["media"],
  };
}

describe("project media editing state", () => {
  it("removes duplicate media while preserving the first occurrence and its order", () => {
    expect(normalizeProjectMedia([projectMedia("first"), projectMedia("second", true), projectMedia("first", true)])).toEqual([
      expect.objectContaining({ display_order: 0, is_cover: false, media: { id: "first" } }),
      expect.objectContaining({ display_order: 1, is_cover: true, media: { id: "second" } }),
    ]);
  });

  it("selects the first item as cover when stale state has no cover", () => {
    expect(normalizeProjectMedia([projectMedia("first"), projectMedia("second")]).map((item) => item.is_cover)).toEqual([true, false]);
  });
});
