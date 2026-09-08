"use client";

import { useSearchParams } from "next/navigation";
import { useTransition } from "react";

import { siteCopy } from "@/content/site";
import { Link, usePathname, useRouter } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { PublicPage, PublicProject, PublicProjectFilters } from "@/lib/public-api";
import { parseView, updateProjectSearch, type ProjectView } from "@/lib/project-filters";

import { ArrowIcon, GridIcon, ListIcon, SearchIcon } from "./icons";
import { ResponsiveImage } from "./responsive-image";

type ProjectArchiveProps = {
  filters: PublicProjectFilters;
  locale: Locale;
  pagination: PublicPage<PublicProject>["pagination"];
  projects: PublicProject[];
};

export function ProjectArchive({ filters, locale, pagination, projects }: ProjectArchiveProps) {
  const copy = siteCopy[locale];
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const query = searchParams.get("q") ?? "";
  const category = searchParams.get("category") ?? "all";
  const discipline = searchParams.get("discipline") ?? "";
  const location = searchParams.get("location") ?? "";
  const status = searchParams.get("status") ?? "";
  const view = parseView(searchParams.get("view"));
  const year = Number.parseInt(searchParams.get("year") ?? "0", 10) || 0;
  const replaceState = (changes: {
    category?: string;
    discipline?: string;
    location?: string;
    offset?: number;
    query?: string;
    status?: string;
    view?: ProjectView;
    year?: number;
  }) => {
    const changesFilters =
      changes.category !== undefined ||
      changes.discipline !== undefined ||
      changes.location !== undefined ||
      changes.query !== undefined ||
      changes.status !== undefined ||
      changes.year !== undefined;
    const serialized = updateProjectSearch(searchParams, {
      ...changes,
      offset: changes.offset ?? (changesFilters ? 0 : undefined),
    });
    startTransition(() => {
      router.replace(serialized ? `${pathname}?${serialized}` : pathname, { scroll: false });
    });
  };

  const formattedCount = new Intl.NumberFormat(locale === "fa" ? "fa-IR" : "en").format(
    pagination.total,
  );
  const previousOffset = Math.max(pagination.offset - pagination.limit, 0);
  const nextOffset = pagination.offset + pagination.limit;
  const hasNextPage = nextOffset < pagination.total;

  return (
    <div aria-busy={isPending}>
      <div className="project-toolbar">
        <label className="project-search">
          <span className="sr-only">{copy.searchPlaceholder}</span>
          <SearchIcon className="control-icon" />
          <input
            onChange={(event) => replaceState({ query: event.target.value })}
            placeholder={copy.searchPlaceholder}
            type="search"
            value={query}
          />
        </label>

        <div aria-label={locale === "fa" ? "فیلتر نوع پروژه" : "Project type filters"} className="project-filters">
          <button
            aria-pressed={category === "all"}
            onClick={() => replaceState({ category: "all" })}
            type="button"
          >
            {locale === "fa" ? "همه" : "All"}
          </button>
          {filters.typologies.map((typology) => (
            <button
              aria-pressed={category === typology.slug}
              key={typology.slug}
              onClick={() => replaceState({ category: typology.slug })}
              type="button"
            >
              {typology.title}
            </button>
          ))}
        </div>

        <p className="project-count" role="status">
          {formattedCount} {pagination.total === 1 ? copy.result : copy.results}
        </p>

        <div aria-label={locale === "fa" ? "شیوه‌ی نمایش" : "View mode"} className="view-switch">
          <button
            aria-pressed={view === "grid"}
            onClick={() => replaceState({ view: "grid" })}
            type="button"
          >
            <GridIcon className="view-icon" />
            {copy.grid}
          </button>
          <button
            aria-pressed={view === "list"}
            onClick={() => replaceState({ view: "list" })}
            type="button"
          >
            <ListIcon className="view-icon" />
            {copy.list}
          </button>
        </div>
      </div>

      <div aria-label={locale === "fa" ? "فیلترهای تکمیلی پروژه" : "Additional project filters"} className="project-filter-controls">
        <label>
          <span>{locale === "fa" ? "تخصص" : "Discipline"}</span>
          <select
            onChange={(event) => replaceState({ discipline: event.target.value })}
            value={discipline}
          >
            <option value="">{locale === "fa" ? "همهٔ تخصص‌ها" : "All disciplines"}</option>
            {filters.disciplines.map((option) => (
              <option key={option.slug} value={option.slug}>
                {option.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>{locale === "fa" ? "وضعیت" : "Status"}</span>
          <select onChange={(event) => replaceState({ status: event.target.value })} value={status}>
            <option value="">{locale === "fa" ? "همهٔ وضعیت‌ها" : "All statuses"}</option>
            {filters.statuses.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>{locale === "fa" ? "مکان" : "Location"}</span>
          <select onChange={(event) => replaceState({ location: event.target.value })} value={location}>
            <option value="">{locale === "fa" ? "همهٔ مکان‌ها" : "All locations"}</option>
            {filters.locations.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>{locale === "fa" ? "سال" : "Year"}</span>
          <select
            onChange={(event) => replaceState({ year: Number.parseInt(event.target.value, 10) || 0 })}
            value={year || ""}
          >
            <option value="">{locale === "fa" ? "همهٔ سال‌ها" : "All years"}</option>
            {filters.years.map((option) => (
              <option key={option} value={option}>
                {new Intl.NumberFormat(locale === "fa" ? "fa-IR" : "en").format(option)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {projects.length > 0 ? (
        <div className="archive-projects" data-view={view}>
          {projects.map((project, index) => (
            <article
              className="archive-project"
              data-category={project.typologies[0]?.slug ?? "project"}
              key={project.slug}
            >
              <Link href={`/projects/${project.slug}`}>
                <div className="archive-project__media">
                  {project.cover_image ? (
                    <ResponsiveImage
                      fill
                      image={project.cover_image}
                      loading={index < 3 ? "eager" : "lazy"}
                      priority={index < 3}
                      sizes={view === "list" ? "38vw" : "(max-width: 767px) 100vw, 34vw"}
                    />
                  ) : null}
                </div>
                <div className="archive-project__meta">
                  <div>
                    <h2>{project.title}</h2>
                    <p>
                      {project.typologies[0]?.title ?? (locale === "fa" ? "پروژه" : "Project")} {" "}
                      <span aria-hidden="true">·</span> {project.completion_year ?? "—"} {" "}
                      <span aria-hidden="true">·</span> {project.location}
                    </p>
                  </div>
                  <ArrowIcon className="directional-icon" />
                </div>
              </Link>
            </article>
          ))}
        </div>
      ) : (
        <div className="archive-empty">
          <p>{copy.noResults}</p>
          <button
            onClick={() =>
              replaceState({
                category: "all",
                discipline: "",
                location: "",
                query: "",
                status: "",
                year: 0,
              })
            }
            type="button"
          >
            {copy.clearFilters}
          </button>
        </div>
      )}

      {pagination.total > pagination.limit ? (
        <nav
          aria-label={locale === "fa" ? "صفحه‌بندی پروژه‌ها" : "Project pagination"}
          className="archive-pagination"
        >
          <button
            disabled={pagination.offset === 0}
            onClick={() => replaceState({ offset: previousOffset })}
            type="button"
          >
            {locale === "fa" ? "پروژه‌های جدیدتر" : "Newer projects"}
          </button>
          <p aria-live="polite">
            {new Intl.NumberFormat(locale === "fa" ? "fa-IR" : "en").format(
              Math.floor(pagination.offset / pagination.limit) + 1,
            )}
          </p>
          <button
            disabled={!hasNextPage}
            onClick={() => replaceState({ offset: nextOffset })}
            type="button"
          >
            {locale === "fa" ? "پروژه‌های قدیمی‌تر" : "Older projects"}
          </button>
        </nav>
      ) : null}
    </div>
  );
}
