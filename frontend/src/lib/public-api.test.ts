import { afterEach, describe, expect, it, vi } from "vitest";

import { getAllProjects } from "./public-api";

describe("complete public archives", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetches every page instead of stopping at the archive default", async () => {
    const upstream = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            items: [{ slug: "first" }],
            pagination: { limit: 24, offset: 0, total: 25 },
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            items: [{ slug: "second" }],
            pagination: { limit: 24, offset: 24, total: 25 },
          }),
          { status: 200 },
        ),
      );
    vi.stubGlobal("fetch", upstream);

    const projects = await getAllProjects("en");

    expect(projects.map((project) => project.slug)).toEqual(["first", "second"]);
    expect(upstream).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/public/projects?locale=en",
      expect.any(Object),
    );
    expect(upstream).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/public/projects?offset=24&locale=en",
      expect.any(Object),
    );
  });
});
