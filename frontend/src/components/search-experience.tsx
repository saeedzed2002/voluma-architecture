"use client";

import { useTransition, type FormEvent } from "react";

import { Link, useRouter } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { PublicSearch } from "@/lib/public-api";

type SearchExperienceProps = {
  locale: Locale;
  search: PublicSearch;
};

const copy = {
  en: {
    clear: "Clear search",
    empty: "No projects or journal articles match this search.",
    hint: "Search the published public archive for projects and journal articles.",
    input: "Search projects and journal",
    results: "results",
    submit: "Search",
  },
  fa: {
    clear: "پاک‌کردن جست‌وجو",
    empty: "هیچ پروژه یا یادداشتی با این جست‌وجو پیدا نشد.",
    hint: "پروژه‌ها و یادداشت‌های منتشرشده را جست‌وجو کنید.",
    input: "جست‌وجوی پروژه‌ها و یادداشت‌ها",
    results: "نتیجه",
    submit: "جست‌وجو",
  },
} as const;

export function SearchExperience({ locale, search }: SearchExperienceProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const labels = copy[locale];

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
          <input defaultValue={search.query} name="q" placeholder={labels.input} type="search" />
        </label>
        <button type="submit">{labels.submit}</button>
      </form>
      {!search.query ? <p className="search-experience__hint">{labels.hint}</p> : null}
      {search.query ? (
        <div className="search-experience__results">
          <p aria-live="polite" role="status">
            {search.items.length} {labels.results}
          </p>
          {search.items.length ? (
            <ol>
              {search.items.map((result) => {
                const href = `/${result.kind === "project" ? "projects" : "journal"}/${result.slug}`;
                const kind =
                  result.kind === "project" ? (locale === "fa" ? "پروژه" : "Project") : locale === "fa" ? "یادداشت" : "Journal";
                return (
                  <li key={`${result.kind}-${result.slug}`}>
                    <Link href={href}>
                      <span>{kind}</span>
                      <h2>{result.title}</h2>
                      <p>{result.summary}</p>
                    </Link>
                  </li>
                );
              })}
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
