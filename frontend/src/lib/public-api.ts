import type { Locale } from "@/i18n/routing";

const apiBaseUrl =
  process.env.VOLUMA_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type PublicImage = {
  alt: string;
  url: string;
};

export type PublicTaxonomy = {
  slug: string;
  title: string;
};

export type PublicProject = {
  completion_year: number | null;
  cover_image: PublicImage | null;
  disciplines: PublicTaxonomy[];
  location: string;
  slug: string;
  status: string | null;
  subtitle: string | null;
  summary: string;
  title: string;
  typologies: PublicTaxonomy[];
};

export type PublicProjectDetail = PublicProject & {
  area: string | null;
  gallery: PublicImage[];
  introduction: PublicEditorialSection | null;
  material: PublicEditorialSection | null;
  narrative: PublicEditorialSection | null;
  quote: string | null;
  scope: string | null;
};

export type PublicEditorialSection = {
  body: string;
  title: string;
};

export type PublicExpertise = {
  display_order: number;
  summary: string;
  title: string;
};

export type PublicProcessStep = PublicExpertise;

export type PublicJournalArticle = {
  body: string[];
  category: PublicTaxonomy;
  cover_image: PublicImage | null;
  excerpt: string;
  published_at: string;
  reading_minutes: number;
  slug: string;
  title: string;
};

export type PublicJournalCard = Omit<PublicJournalArticle, "body">;

export type PublicHome = {
  expertise: PublicExpertise[];
  hero_body: string;
  hero_image: PublicImage | null;
  hero_title: string;
  journal: PublicJournalCard[];
  process: PublicProcessStep[];
  selected_projects: PublicProject[];
  studio_name: string;
};

export type PublicStudio = {
  intro: string;
  members: { biography: string | null; name: string; role: string }[];
  principles: { body: string; title: string }[];
  recognitions: string[];
};

export type PublicSite = {
  privacy: string;
  studio_name: string;
};

export type PublicSearch = {
  items: { kind: "project" | "journal"; slug: string; summary: string; title: string }[];
  query: string;
};

export type PublicPage<T> = {
  items: T[];
  pagination: { limit: number; offset: number; total: number };
};

export class PublicApiError extends Error {
  constructor(
    public readonly status: number,
    path: string,
  ) {
    super(`VOLUMA public API request failed (${status}) for ${path}`);
  }
}

async function publicFetch<T>(path: string, locale: Locale): Promise<T> {
  const separator = path.includes("?") ? "&" : "?";
  const response = await fetch(`${apiBaseUrl}/api/v1/public${path}${separator}locale=${locale}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new PublicApiError(response.status, path);
  return (await response.json()) as T;
}

export function getHome(locale: Locale) {
  return publicFetch<PublicHome>("/home", locale);
}

export function getProjects(locale: Locale) {
  return publicFetch<PublicPage<PublicProject>>("/projects", locale);
}

export function getProject(locale: Locale, slug: string) {
  return publicFetch<PublicProjectDetail>(`/projects/${encodeURIComponent(slug)}`, locale);
}

export function getExpertise(locale: Locale) {
  return publicFetch<PublicExpertise[]>("/expertise", locale);
}

export function getProcess(locale: Locale) {
  return publicFetch<PublicProcessStep[]>("/process", locale);
}

export function getStudio(locale: Locale) {
  return publicFetch<PublicStudio>("/studio", locale);
}

export function getJournal(locale: Locale) {
  return publicFetch<PublicPage<PublicJournalCard>>("/journal", locale);
}

export function getArticle(locale: Locale, slug: string) {
  return publicFetch<PublicJournalArticle>(`/journal/${encodeURIComponent(slug)}`, locale);
}

export function getSite(locale: Locale) {
  return publicFetch<PublicSite>("/site", locale);
}

export function getSearch(locale: Locale, query: string) {
  return publicFetch<PublicSearch>(`/search?q=${encodeURIComponent(query)}`, locale);
}
