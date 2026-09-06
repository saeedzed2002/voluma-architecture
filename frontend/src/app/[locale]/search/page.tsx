import type { Metadata } from "next";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import { EditorialHeader } from "@/components/editorial-header";
import { FixtureNotice } from "@/components/fixture-notice";
import { SearchExperience } from "@/components/search-experience";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { getSearch } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type SearchPageProps = {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ q?: string }>;
};

export async function generateMetadata({ params }: SearchPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  const title = currentLocale === "fa" ? "جست‌وجو" : "Search";
  const description =
    currentLocale === "fa"
      ? "جست‌وجو در پروژه‌ها و یادداشت‌های منتشرشده."
      : "Search published projects and journal articles.";

  return {
    ...(await publicMetadata({ description, locale: currentLocale, path: "/search", title })),
    robots: { follow: false, index: false },
  };
}

export default async function SearchPage({ params, searchParams }: SearchPageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const copy = siteCopy[locale];
  const query = (await searchParams).q?.trim() ?? "";
  const search = query ? await getSearch(locale, query) : { items: [], query: "" };

  return (
    <main className="editorial-page section-shell search-page">
      <EditorialHeader
        eyebrow={locale === "fa" ? "جست‌وجو" : "Search"}
        intro={
          locale === "fa"
            ? "پروژه‌ها و یادداشت‌های عمومی را با عنوان، مکان و موضوع جست‌وجو کنید."
            : "Search the public project and journal archive by title, place, and subject."
        }
        title={locale === "fa" ? "برای یافتن یک مسیر." : "Find a line of thought."}
      />
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      <Suspense
        fallback={
          <p className="search-experience__hint">
            {locale === "fa" ? "در حال آماده‌سازی جست‌وجو…" : "Preparing search…"}
          </p>
        }
      >
        <SearchExperience locale={locale} search={search} />
      </Suspense>
    </main>
  );
}
