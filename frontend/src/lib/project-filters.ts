import type { Locale } from "@/i18n/routing";
import type { PublicProject } from "@/lib/public-api";

export type ProjectCategory = "residential" | "workspace" | "cultural" | "adaptive-reuse";

export type ProjectView = "grid" | "list";
export type CategoryFilter = "all" | ProjectCategory;

const categories = new Set<CategoryFilter>([
  "all",
  "residential",
  "workspace",
  "cultural",
  "adaptive-reuse",
]);

export function parseCategory(value: string | null): CategoryFilter {
  return value && categories.has(value as CategoryFilter) ? (value as CategoryFilter) : "all";
}

export function parseView(value: string | null): ProjectView {
  return value === "list" ? "list" : "grid";
}

export function filterProjects(
  projects: PublicProject[],
  locale: Locale,
  query: string,
  category: CategoryFilter,
): PublicProject[] {
  const normalized = query.trim().toLocaleLowerCase(locale);

  return projects.filter((project) => {
    const inCategory =
      category === "all" || project.typologies.some((typology) => typology.slug === category);
    if (!normalized) return inCategory;

    const searchable = [
      project.title,
      project.summary,
      project.location,
      project.completion_year,
    ]
      .join(" ")
      .toLocaleLowerCase(locale);

    return inCategory && searchable.includes(normalized);
  });
}

export function updateProjectSearch(
  current: URLSearchParams,
  changes: { query?: string; category?: CategoryFilter; view?: ProjectView },
): string {
  const next = new URLSearchParams(current);

  if (changes.query !== undefined) {
    const value = changes.query.trim();
    if (value) next.set("q", value);
    else next.delete("q");
  }

  if (changes.category !== undefined) {
    if (changes.category === "all") next.delete("category");
    else next.set("category", changes.category);
  }

  if (changes.view !== undefined) {
    if (changes.view === "grid") next.delete("view");
    else next.set("view", changes.view);
  }

  return next.toString();
}
