export type Administrator = {
  email: string;
  id: string;
};

export type AdminSession = {
  administrator: Administrator;
  csrf_token: string;
};

export type AdminDashboard = {
  journal_articles: Record<"draft" | "published", number>;
  projects: Record<"draft" | "published", number>;
};

export type AdminTaxonomy = {
  display_order: number;
  id: string;
  slug: string;
  title_en: string;
  title_fa: string;
};

export type AdminBilingualContent = {
  display_order: number;
  id: string;
  publication_state: "draft" | "published";
  summary_en: string;
  summary_fa: string;
  title_en: string;
  title_fa: string;
  updated_at: string;
};

export type AdminBilingualContentWrite = Pick<
  AdminBilingualContent,
  "publication_state" | "summary_en" | "summary_fa" | "title_en" | "title_fa"
>;

export type AdminBilingualContentKind = "expertise" | "process";

export type AdminStudioContentKind = "people" | "recognition";

export type AdminStudioMember = {
  biography_en: string | null;
  biography_fa: string | null;
  display_order: number;
  id: string;
  name: string;
  publication_state: "draft" | "published";
  role_en: string;
  role_fa: string;
  updated_at: string;
};

export type AdminRecognition = {
  display_order: number;
  id: string;
  publication_state: "draft" | "published";
  title_en: string;
  title_fa: string;
  updated_at: string;
};

export type AdminStudioContent = AdminStudioMember | AdminRecognition;

export type AdminJournalCategory = {
  display_order: number;
  id: string;
  slug: string;
  title_en: string;
  title_fa: string;
};

export type AdminJournalArticleBlock =
  | {
      block_type: "quote";
      content_en: { attribution?: string; quote: string };
      content_fa: { attribution?: string; quote: string };
      display_order: number;
      id: string;
    }
  | {
      block_type: "text";
      content_en: { body: string; heading?: string };
      content_fa: { body: string; heading?: string };
      display_order: number;
      id: string;
    };

export type JournalArticleBlockWrite =
  | {
      block_type: "quote";
      content_en: { attribution?: string; quote: string };
      content_fa: { attribution?: string; quote: string };
    }
  | {
      block_type: "text";
      content_en: { body: string; heading?: string };
      content_fa: { body: string; heading?: string };
    };

export type AdminJournalArticleListItem = {
  category: AdminJournalCategory;
  id: string;
  publication_state: "draft" | "published";
  published_at: string | null;
  slug: string;
  title_en: string;
  title_fa: string;
  updated_at: string;
};

export type AdminJournalArticle = AdminJournalArticleListItem & {
  blocks: AdminJournalArticleBlock[];
  cover_alt_en: string | null;
  cover_alt_fa: string | null;
  cover_image_url: string | null;
  excerpt_en: string;
  excerpt_fa: string;
  reading_minutes: number;
  seo_description_en: string | null;
  seo_description_fa: string | null;
  seo_title_en: string | null;
  seo_title_fa: string | null;
};

export type JournalArticleWrite = {
  blocks: JournalArticleBlockWrite[];
  category_id: string;
  cover_alt_en: string | null;
  cover_alt_fa: string | null;
  cover_image_url: string | null;
  excerpt_en: string;
  excerpt_fa: string;
  publication_state: "draft" | "published";
  published_at: string | null;
  reading_minutes: number;
  seo_description_en: string | null;
  seo_description_fa: string | null;
  seo_title_en: string | null;
  seo_title_fa: string | null;
  title_en: string;
  title_fa: string;
};

export type AdminProjectBlock =
  | { block_type: "quote"; content_en: { attribution?: string; quote: string }; content_fa: { attribution?: string; quote: string }; display_order: number; id: string }
  | { block_type: "text"; content_en: { body: string; heading?: string }; content_fa: { body: string; heading?: string }; display_order: number; id: string }
  | { block_type: "single_image" | "full_width_image"; content_en: { media_id: string }; content_fa: { media_id: string }; display_order: number; id: string }
  | { block_type: "paired_image"; content_en: { left_media_id: string; right_media_id: string }; content_fa: { left_media_id: string; right_media_id: string }; display_order: number; id: string }
  | { block_type: "gallery"; content_en: { media_ids: string[] }; content_fa: { media_ids: string[] }; display_order: number; id: string };

export type AdminProjectListItem = {
  display_order: number;
  featured: boolean;
  id: string;
  publication_state: "draft" | "published";
  published_at: string | null;
  slug: string;
  title_en: string;
  title_fa: string;
  updated_at: string;
};

export type AdminProject = AdminProjectListItem & {
  area_en: string | null;
  area_fa: string | null;
  architect_en: string | null;
  architect_fa: string | null;
  blocks: AdminProjectBlock[];
  client_en: string | null;
  client_fa: string | null;
  collaborators_en: string | null;
  collaborators_fa: string | null;
  completion_date: string | null;
  completion_year: number | null;
  disciplines: AdminTaxonomy[];
  intro_en: string | null;
  intro_fa: string | null;
  intro_title_en: string | null;
  intro_title_fa: string | null;
  location_en: string;
  location_fa: string;
  material_en: string | null;
  material_fa: string | null;
  material_title_en: string | null;
  material_title_fa: string | null;
  narrative_en: string | null;
  narrative_fa: string | null;
  narrative_title_en: string | null;
  narrative_title_fa: string | null;
  quote_en: string | null;
  quote_fa: string | null;
  scope_en: string | null;
  scope_fa: string | null;
  seo_description_en: string | null;
  seo_description_fa: string | null;
  seo_title_en: string | null;
  seo_title_fa: string | null;
  status_en: string | null;
  status_fa: string | null;
  subtitle_en: string | null;
  subtitle_fa: string | null;
  summary_en: string;
  summary_fa: string;
  title_en: string;
  title_fa: string;
  typologies: AdminTaxonomy[];
};

export type AdminProjectFormOptions = {
  disciplines: AdminTaxonomy[];
  typologies: AdminTaxonomy[];
};

export type ProjectBlockWrite =
  | { block_type: "quote"; content_en: { attribution?: string; quote: string }; content_fa: { attribution?: string; quote: string } }
  | { block_type: "text"; content_en: { body: string; heading?: string }; content_fa: { body: string; heading?: string } }
  | { block_type: "single_image" | "full_width_image"; content_en: { media_id: string }; content_fa: { media_id: string } }
  | { block_type: "paired_image"; content_en: { left_media_id: string; right_media_id: string }; content_fa: { left_media_id: string; right_media_id: string } }
  | { block_type: "gallery"; content_en: { media_ids: string[] }; content_fa: { media_ids: string[] } };

export type ProjectWrite = Omit<
  AdminProject,
  | "blocks"
  | "display_order"
  | "id"
  | "published_at"
  | "slug"
  | "updated_at"
  | "disciplines"
  | "typologies"
> & {
  discipline_ids: string[];
  published_at: string | null;
  typology_ids: string[];
};

export class AdminApiError extends Error {
  constructor(public readonly status: number) {
    super(`VOLUMA administrator API request failed (${status})`);
  }
}

type RequestOptions = {
  body?: unknown;
  csrfToken?: string;
  method?: "DELETE" | "GET" | "PATCH" | "POST" | "PUT";
};

async function adminFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers({ Accept: "application/json" });
  if (options.body !== undefined) headers.set("Content-Type", "application/json");
  if (options.csrfToken !== undefined) headers.set("X-VOLUMA-CSRF", options.csrfToken);

  const response = await fetch(`/api/v1/admin${path}`, {
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    cache: "no-store",
    credentials: "same-origin",
    headers,
    method: options.method ?? "GET",
  });
  if (!response.ok) throw new AdminApiError(response.status);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function getAdminSession() {
  return adminFetch<AdminSession>("/auth/me");
}

export function loginAdministrator(email: string, password: string) {
  return adminFetch<AdminSession>("/auth/login", { body: { email, password }, method: "POST" });
}

export function logoutAdministrator(csrfToken: string) {
  return adminFetch<void>("/auth/logout", { csrfToken, method: "POST" });
}

export function getAdminDashboard() {
  return adminFetch<AdminDashboard>("/dashboard");
}

export function getAdminProjects() {
  return adminFetch<{ items: AdminProjectListItem[] }>("/projects");
}

export function getAdminProject(projectId: string) {
  return adminFetch<AdminProject>(`/projects/${encodeURIComponent(projectId)}`);
}

export function getAdminProjectFormOptions() {
  return adminFetch<AdminProjectFormOptions>("/projects/form-options");
}

export function createAdminProject(payload: ProjectWrite & { slug: string }, csrfToken: string) {
  return adminFetch<AdminProject>("/projects", { body: payload, csrfToken, method: "POST" });
}

export function updateAdminProject(projectId: string, payload: ProjectWrite, csrfToken: string) {
  return adminFetch<AdminProject>(`/projects/${encodeURIComponent(projectId)}`, {
    body: payload,
    csrfToken,
    method: "PUT",
  });
}

export function replaceAdminProjectBlocks(
  projectId: string,
  blocks: ProjectBlockWrite[],
  csrfToken: string,
) {
  return adminFetch<AdminProject>(`/projects/${encodeURIComponent(projectId)}/blocks`, {
    body: { blocks },
    csrfToken,
    method: "PUT",
  });
}

export function reorderAdminProjects(projectIds: string[], csrfToken: string) {
  return adminFetch<{ items: AdminProjectListItem[] }>("/projects/order", {
    body: { project_ids: projectIds },
    csrfToken,
    method: "PUT",
  });
}

export function deleteAdminProject(projectId: string, csrfToken: string) {
  return adminFetch<void>(`/projects/${encodeURIComponent(projectId)}`, {
    csrfToken,
    method: "DELETE",
  });
}

export function getAdminTaxonomies(kind: "disciplines" | "typologies") {
  return adminFetch<{ items: AdminTaxonomy[] }>(`/${kind}`);
}

export function createAdminTaxonomy(
  kind: "disciplines" | "typologies",
  payload: Pick<AdminTaxonomy, "slug" | "title_en" | "title_fa">,
  csrfToken: string,
) {
  return adminFetch<AdminTaxonomy>(`/${kind}`, { body: payload, csrfToken, method: "POST" });
}

export function reorderAdminTaxonomies(
  kind: "disciplines" | "typologies",
  identifiers: string[],
  csrfToken: string,
) {
  return adminFetch<{ items: AdminTaxonomy[] }>(`/${kind}/order`, {
    body: { identifiers },
    csrfToken,
    method: "PUT",
  });
}

export function updateAdminTaxonomy(
  kind: "disciplines" | "typologies",
  identifier: string,
  payload: Pick<AdminTaxonomy, "slug" | "title_en" | "title_fa">,
  csrfToken: string,
) {
  return adminFetch<AdminTaxonomy>(`/${kind}/${encodeURIComponent(identifier)}`, {
    body: payload,
    csrfToken,
    method: "PUT",
  });
}

export function deleteAdminTaxonomy(
  kind: "disciplines" | "typologies",
  identifier: string,
  csrfToken: string,
) {
  return adminFetch<void>(`/${kind}/${encodeURIComponent(identifier)}`, {
    csrfToken,
    method: "DELETE",
  });
}

export function getAdminBilingualContent(kind: AdminBilingualContentKind) {
  return adminFetch<{ items: AdminBilingualContent[] }>(`/${kind}`);
}

export function createAdminBilingualContent(
  kind: AdminBilingualContentKind,
  payload: Partial<AdminBilingualContentWrite>,
  csrfToken: string,
) {
  return adminFetch<AdminBilingualContent>(`/${kind}`, {
    body: payload,
    csrfToken,
    method: "POST",
  });
}

export function updateAdminBilingualContent(
  kind: AdminBilingualContentKind,
  identifier: string,
  payload: AdminBilingualContentWrite,
  csrfToken: string,
) {
  return adminFetch<AdminBilingualContent>(`/${kind}/${encodeURIComponent(identifier)}`, {
    body: payload,
    csrfToken,
    method: "PUT",
  });
}

export function reorderAdminBilingualContent(
  kind: AdminBilingualContentKind,
  identifiers: string[],
  csrfToken: string,
) {
  return adminFetch<{ items: AdminBilingualContent[] }>(`/${kind}/order`, {
    body: { identifiers },
    csrfToken,
    method: "PUT",
  });
}

export function deleteAdminBilingualContent(
  kind: AdminBilingualContentKind,
  identifier: string,
  csrfToken: string,
) {
  return adminFetch<void>(`/${kind}/${encodeURIComponent(identifier)}`, {
    csrfToken,
    method: "DELETE",
  });
}

export function getAdminStudioContent(kind: AdminStudioContentKind) {
  return adminFetch<{ items: AdminStudioContent[] }>(`/${kind}`);
}

export function createAdminStudioContent(
  kind: AdminStudioContentKind,
  payload: Record<string, string | null>,
  csrfToken: string,
) {
  return adminFetch<AdminStudioContent>(`/${kind}`, { body: payload, csrfToken, method: "POST" });
}

export function updateAdminStudioContent(
  kind: AdminStudioContentKind,
  identifier: string,
  payload: Record<string, string | null>,
  csrfToken: string,
) {
  return adminFetch<AdminStudioContent>(`/${kind}/${encodeURIComponent(identifier)}`, {
    body: payload,
    csrfToken,
    method: "PUT",
  });
}

export function reorderAdminStudioContent(
  kind: AdminStudioContentKind,
  identifiers: string[],
  csrfToken: string,
) {
  return adminFetch<{ items: AdminStudioContent[] }>(`/${kind}/order`, {
    body: { identifiers },
    csrfToken,
    method: "PUT",
  });
}

export function deleteAdminStudioContent(
  kind: AdminStudioContentKind,
  identifier: string,
  csrfToken: string,
) {
  return adminFetch<void>(`/${kind}/${encodeURIComponent(identifier)}`, {
    csrfToken,
    method: "DELETE",
  });
}

export function getAdminJournalCategories() {
  return adminFetch<{ items: AdminJournalCategory[] }>("/journal/categories");
}

export function createAdminJournalCategory(
  payload: Pick<AdminJournalCategory, "slug" | "title_en" | "title_fa">,
  csrfToken: string,
) {
  return adminFetch<AdminJournalCategory>("/journal/categories", {
    body: payload,
    csrfToken,
    method: "POST",
  });
}

export function updateAdminJournalCategory(
  identifier: string,
  payload: Pick<AdminJournalCategory, "slug" | "title_en" | "title_fa">,
  csrfToken: string,
) {
  return adminFetch<AdminJournalCategory>(`/journal/categories/${encodeURIComponent(identifier)}`, {
    body: payload,
    csrfToken,
    method: "PUT",
  });
}

export function reorderAdminJournalCategories(identifiers: string[], csrfToken: string) {
  return adminFetch<{ items: AdminJournalCategory[] }>("/journal/categories/order", {
    body: { identifiers },
    csrfToken,
    method: "PUT",
  });
}

export function deleteAdminJournalCategory(identifier: string, csrfToken: string) {
  return adminFetch<void>(`/journal/categories/${encodeURIComponent(identifier)}`, {
    csrfToken,
    method: "DELETE",
  });
}

export function getAdminJournalArticles() {
  return adminFetch<{ items: AdminJournalArticleListItem[] }>("/journal/articles");
}

export function getAdminJournalArticle(identifier: string) {
  return adminFetch<AdminJournalArticle>(`/journal/articles/${encodeURIComponent(identifier)}`);
}

export function createAdminJournalArticle(
  payload: JournalArticleWrite & { slug: string },
  csrfToken: string,
) {
  return adminFetch<AdminJournalArticle>("/journal/articles", {
    body: payload,
    csrfToken,
    method: "POST",
  });
}

export function updateAdminJournalArticle(
  identifier: string,
  payload: JournalArticleWrite,
  csrfToken: string,
) {
  return adminFetch<AdminJournalArticle>(`/journal/articles/${encodeURIComponent(identifier)}`, {
    body: payload,
    csrfToken,
    method: "PUT",
  });
}

export function deleteAdminJournalArticle(identifier: string, csrfToken: string) {
  return adminFetch<void>(`/journal/articles/${encodeURIComponent(identifier)}`, {
    csrfToken,
    method: "DELETE",
  });
}
