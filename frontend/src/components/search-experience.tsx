"use client";

import { useMemo, useTransition, type FormEvent } from "react";
import { useSearchParams } from "next/navigation";

import { journalArticles } from "@/content/public-pages";
import { localize, projects } from "@/content/site";
import { Link, useRouter } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";

type SearchExperienceProps = {
  locale: Locale;
};

type SearchResult = {
  href: string;
  kind: string;
  summary: string;
  title: string;
};

const copy = {
  en: {
    clear: "Clear search",
    empty: "No projects or journal articles match this search.",
    hint: "Search the development fixtures for projects and journal articles.",
    input: "Search projects and journal",
    results: "results",
    submit: "Search",
  },
  fa: {
    clear: "پاک‌کردن جست‌وجو",
    empty: "هیچ پروژه یا یادداشتی با این جست‌وجو پیدا نشد.",
    hint: "پروژه‌ها و یادداشت‌های نمونهٔ توسعه را جست‌وجو کنید.",
    input: "جست‌وجوی پروژه‌ها و یادداشت‌ها",
    results: "نتیجه",
    submit: "جست‌وجو",
  },
} as const;

export function SearchExperience({ locale }: SearchExperienceProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const query = searchParams.get("q")?.trim() ?? "";
  const labels = copy[locale];
  const results = useMemo(() => {
    if (!query) return [];
    const normalized = query.toLocaleLowerCase(locale);
    const projectResults: SearchResult[] = projects
      .filter((project) =>
        [project.title[locale], project.summary[locale], project.location[locale], project.year]
          .join(" ")
          .toLocaleLowerCase(locale)
          .includes(normalized),
      )
      .map((project) => ({
        href: `/projects/${project.slug}`,
        kind: locale === "fa" ? "پروژه" : "Project",
        summary: localize(project.summary, locale),
        title: localize(project.title, locale),
      }));
    const articleResults: SearchResult[] = journalArticles
      .filter((article) =>
        [article.title[locale], article.excerpt[locale], article.category[locale]]
          .join(" ")
          .toLocaleLowerCase(locale)
          .includes(normalized),
      )
      .map((article) => ({
        href: `/journal/${article.slug}`,
        kind: locale === "fa" ? "یادداشت" : "Journal",
        summary: localize(article.excerpt, locale),
        title: localize(article.title, locale),
      }));

    return [...projectResults, ...articleResults];
  }, [locale, query]);

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const nextQuery = String(formData.get("q") ?? "").trim();
    const href = nextQuery ? `/search?q=${encodeURIComponent(nextQuery)}` : "/search";
    startTransition(() => router.replace(href, { scroll: false }));
  };

  return (
    <div aria-busy={isPending} className="search-experience">
      <form onSubmit={submitSearch} role="search">
        <label>
          <span className="sr-only">{labels.input}</span>
          <input defaultValue={query} name="q" placeholder={labels.input} type="search" />
        </label>
        <button type="submit">{labels.submit}</button>
      </form>
      {!query ? <p className="search-experience__hint">{labels.hint}</p> : null}
      {query ? (
        <div className="search-experience__results">
          <p aria-live="polite" role="status">
            {results.length} {labels.results}
          </p>
          {results.length ? (
            <ol>
              {results.map((result) => (
                <li key={result.href}>
                  <Link href={result.href}>
                    <span>{result.kind}</span>
                    <h2>{result.title}</h2>
                    <p>{result.summary}</p>
                  </Link>
                </li>
              ))}
            </ol>
          ) : (
            <p>{labels.empty}</p>
          )}
          <Link className="text-link" href="/search">
            {labels.clear}
          </Link>
        </div>
      ) : null}
    </div>
  );
}
