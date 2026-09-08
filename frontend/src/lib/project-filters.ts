export type ProjectView = "grid" | "list";

export function parseView(value: string | null): ProjectView {
  return value === "list" ? "list" : "grid";
}

export function updateProjectSearch(
  current: URLSearchParams,
  changes: {
    category?: string;
    discipline?: string;
    location?: string;
    offset?: number;
    query?: string;
    status?: string;
    view?: ProjectView;
    year?: number;
  },
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

  for (const [key, value] of Object.entries({
    discipline: changes.discipline,
    location: changes.location,
    status: changes.status,
  })) {
    if (value === undefined) continue;
    if (value) next.set(key, value);
    else next.delete(key);
  }

  if (changes.view !== undefined) {
    if (changes.view === "grid") next.delete("view");
    else next.set("view", changes.view);
  }

  if (changes.offset !== undefined) {
    if (changes.offset > 0) next.set("offset", String(changes.offset));
    else next.delete("offset");
  }

  if (changes.year !== undefined) {
    if (changes.year > 0) next.set("year", String(changes.year));
    else next.delete("year");
  }

  return next.toString();
}
