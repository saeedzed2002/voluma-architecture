import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { EditorialHeader } from "@/components/editorial-header";
import { FixtureNotice } from "@/components/fixture-notice";
import { ArrowIcon } from "@/components/icons";
import { Reveal } from "@/components/reveal";
import { siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { getJournal } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type JournalPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: JournalPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  const title = currentLocale === "fa" ? "یادداشت‌ها" : "Journal";
  const description =
    currentLocale === "fa"
      ? "یادداشت‌های ولوما دربارهٔ معماری، طراحی و فرایند."
      : "VOLUMA notes on architecture, design, and process.";

  return publicMetadata({ description, locale: currentLocale, path: "/journal", title });
}

export default async function JournalPage({ params }: JournalPageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const copy = siteCopy[locale];
  const journal = await getJournal(locale);

  return (
    <main className="editorial-page section-shell">
      <EditorialHeader
        eyebrow={locale === "fa" ? "یادداشت‌ها" : "Journal"}
        intro={
          locale === "fa"
            ? "یادداشت‌هایی دربارهٔ مکان، مصالح و شیوه‌هایی که یک فضا در طول زمان خوانده می‌شود."
            : "Notes on place, material, and the ways a space is read over time."
        }
        title={locale === "fa" ? "برای خواندنِ میان پروژه‌ها." : "Reading between projects."}
      />
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      <section
        aria-label={locale === "fa" ? "فهرست یادداشت‌ها" : "Journal archive"}
        className="journal-archive"
      >
        {journal.items.map((article, index) => (
          <Reveal className="journal-archive__entry" delay={index * 0.06} key={article.slug}>
            <article>
              <Link href={`/journal/${article.slug}`}>
                <div className="journal-archive__media">
                  {article.cover_image ? (
                    <Image
                      alt={article.cover_image.alt}
                      fill
                      priority={index === 0}
                      sizes="(max-width: 767px) 100vw, 38vw"
                      src={article.cover_image.url}
                    />
                  ) : null}
                </div>
                <div className="journal-archive__copy">
                  <p>
                    {article.category.title} <span aria-hidden="true">·</span> {article.reading_minutes}{" "}
                    {locale === "fa" ? "دقیقه مطالعه" : "min read"}
                  </p>
                  <h2>{article.title}</h2>
                  <p>{article.excerpt}</p>
                  <ArrowIcon className="directional-icon" />
                </div>
              </Link>
            </article>
          </Reveal>
        ))}
      </section>
    </main>
  );
}
