import { describe, expect, it } from "vitest";

import { parseView, updateProjectSearch } from "./project-filters";

describe("project archive state", () => {
  it("parses only supported view state", () => {
    expect(parseView("list")).toBe("list");
    expect(parseView("cards")).toBe("grid");
  });

  it("serializes defaults out of the URL", () => {
    const current = new URLSearchParams(
      "q=house&category=residential&discipline=architecture&status=Completed&location=Tehran&year=2026&offset=12&view=list",
    );
    expect(
      updateProjectSearch(current, {
        category: "all",
        discipline: "",
        location: "",
        offset: 0,
        query: "",
        status: "",
        view: "grid",
        year: 0,
      }),
    ).toBe("");
  });

  it("keeps server-backed filters and an archive page in a shareable URL", () => {
    const current = new URLSearchParams("category=workspace");
    expect(updateProjectSearch(current, { discipline: "architecture", offset: 24 })).toBe(
      "category=workspace&discipline=architecture&offset=24",
    );
  });
});
