import type { Metadata } from "next";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import { FixtureNotice } from "@/components/fixture-notice";
import { ProjectArchive } from "@/components/project-archive";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { getProjects } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type ProjectsPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: ProjectsPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};

  const currentLocale = locale as Locale;
  return publicMetadata({
    description: siteCopy[currentLocale].archiveIntro,
    locale: currentLocale,
    path: "/projects",
    title: siteCopy[currentLocale].archiveTitle,
  });
}

export default async function ProjectsPage({ params }: ProjectsPageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const copy = siteCopy[locale];
  const archive = await getProjects(locale);

  return (
    <main className="archive-page section-shell">
      <header className="archive-page__header">
        <h1>{copy.archiveTitle}</h1>
        <p>{copy.archiveIntro}</p>
      </header>
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      <Suspense
        fallback={
          <p aria-live="polite" className="archive-loading">
            {locale === "fa" ? "در حال آماده‌سازی آرشیو…" : "Preparing the archive…"}
          </p>
        }
      >
        <ProjectArchive locale={locale} projects={archive.items} />
      </Suspense>
    </main>
  );
}
