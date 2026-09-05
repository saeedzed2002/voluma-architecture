import { describe, expect, it } from "vitest";

import { projects } from "@/content/site";

import { filterProjects, parseCategory, parseView, updateProjectSearch } from "./project-filters";

describe("project archive state", () => {
  it("parses only supported URL state", () => {
    expect(parseCategory("workspace")).toBe("workspace");
    expect(parseCategory("unknown")).toBe("all");
    expect(parseView("list")).toBe("list");
    expect(parseView("cards")).toBe("grid");
  });

  it("filters localized project content", () => {
    expect(filterProjects(projects, "en", "Karaj", "all")).toHaveLength(2);
    expect(filterProjects(projects, "fa", "حیاط", "residential")).toHaveLength(1);
    expect(filterProjects(projects, "en", "", "cultural")).toHaveLength(1);
  });

  it("serializes defaults out of the URL", () => {
    const current = new URLSearchParams("q=house&category=residential&view=list");
    expect(updateProjectSearch(current, { query: "", category: "all", view: "grid" })).toBe("");
  });
});
