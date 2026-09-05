import { describe, expect, it } from "vitest";

import type { PublicProject } from "@/lib/public-api";

import { filterProjects, parseCategory, parseView, updateProjectSearch } from "./project-filters";

const projects: PublicProject[] = [
  {
    completion_year: 2026,
    cover_image: null,
    disciplines: [],
    location: "Karaj",
    slug: "atelier",
    status: "Completed",
    subtitle: null,
    summary: "Shared space for focused work.",
    title: "Northline Atelier",
    typologies: [{ slug: "workspace", title: "Workspace" }],
  },
  {
    completion_year: 2025,
    cover_image: null,
    disciplines: [],
    location: "تهران",
    slug: "courtyard",
    status: "تکمیل‌شده",
    subtitle: null,
    summary: "خانه‌ای پیرامون حیاط.",
    title: "خانه‌ی حیاط مرکزی",
    typologies: [{ slug: "residential", title: "مسکونی" }],
  },
  {
    completion_year: 2025,
    cover_image: null,
    disciplines: [],
    location: "Shiraz",
    slug: "passage",
    status: "Competition",
    subtitle: null,
    summary: "Shaded civic rooms.",
    title: "Cedar Passage",
    typologies: [{ slug: "cultural", title: "Cultural" }],
  },
];

describe("project archive state", () => {
  it("parses only supported URL state", () => {
    expect(parseCategory("workspace")).toBe("workspace");
    expect(parseCategory("unknown")).toBe("all");
    expect(parseView("list")).toBe("list");
    expect(parseView("cards")).toBe("grid");
  });

  it("filters API project content", () => {
    expect(filterProjects(projects, "en", "Karaj", "all")).toHaveLength(1);
    expect(filterProjects(projects, "fa", "حیاط", "residential")).toHaveLength(1);
    expect(filterProjects(projects, "en", "", "cultural")).toHaveLength(1);
  });

  it("serializes defaults out of the URL", () => {
    const current = new URLSearchParams("q=house&category=residential&view=list");
    expect(updateProjectSearch(current, { query: "", category: "all", view: "grid" })).toBe("");
  });
});
