"use client";

import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { useMemo, useTransition } from "react";

import type { Project } from "@/content/site";
import { categoryLabels, localize, siteCopy } from "@/content/site";
import { Link, usePathname, useRouter } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { formatYear } from "@/lib/locale";
import {
  filterProjects,
  parseCategory,
  parseView,
  updateProjectSearch,
  type CategoryFilter,
  type ProjectView,
} from "@/lib/project-filters";

import { ArrowIcon, GridIcon, ListIcon, SearchIcon } from "./icons";

const categoryOrder: CategoryFilter[] = [
  "all",
  "residential",
  "workspace",
  "cultural",
  "adaptive-reuse",
];

type ProjectArchiveProps = {
  locale: Locale;
  projects: Project[];
};

export function ProjectArchive({ locale, projects }: ProjectArchiveProps) {
  const copy = siteCopy[locale];
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const query = searchParams.get("q") ?? "";
  const category = parseCategory(searchParams.get("category"));
  const view = parseView(searchParams.get("view"));
  const visibleProjects = useMemo(
    () => filterProjects(projects, locale, query, category),
    [category, locale, projects, query],
  );

  const replaceState = (changes: {
    query?: string;
    category?: CategoryFilter;
    view?: ProjectView;
  }) => {
    const serialized = updateProjectSearch(searchParams, changes);
    startTransition(() => {
      router.replace(serialized ? `${pathname}?${serialized}` : pathname, { scroll: false });
    });
  };

  const formattedCount = new Intl.NumberFormat(locale === "fa" ? "fa-IR" : "en").format(
    visibleProjects.length,
  );

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

        <div
          aria-label={locale === "fa" ? "فیلتر نوع پروژه" : "Project type filters"}
          className="project-filters"
        >
          {categoryOrder.map((value) => (
            <button
              aria-pressed={category === value}
              key={value}
              onClick={() => replaceState({ category: value })}
              type="button"
            >
              {categoryLabels[value][locale]}
            </button>
          ))}
        </div>

        <p className="project-count" role="status">
          {formattedCount} {visibleProjects.length === 1 ? copy.result : copy.results}
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

      {visibleProjects.length > 0 ? (
        <div className="archive-projects" data-view={view}>
          {visibleProjects.map((project, index) => (
            <article
              className="archive-project"
              data-category={project.category}
              key={project.slug}
            >
              <Link href={`/projects/${project.slug}`}>
                <div className="archive-project__media">
                  <Image
                    alt={localize(project.alt, locale)}
                    fill
                    priority={index < 3}
                    sizes={view === "list" ? "38vw" : "(max-width: 767px) 100vw, 34vw"}
                    src={project.image}
                    style={{ objectPosition: project.imagePosition ?? "center" }}
                  />
                </div>
                <div className="archive-project__meta">
                  <div>
                    <h2>{localize(project.title, locale)}</h2>
                    <p>
                      {localize(project.categoryLabel, locale)} <span aria-hidden="true">·</span>{" "}
                      {formatYear(project.year, locale)} <span aria-hidden="true">·</span>{" "}
                      {localize(project.location, locale)}
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
          <button onClick={() => replaceState({ query: "", category: "all" })} type="button">
            {copy.clearFilters}
          </button>
        </div>
      )}
    </div>
  );
}
