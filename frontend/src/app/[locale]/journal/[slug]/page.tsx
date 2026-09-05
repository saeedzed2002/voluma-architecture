import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { FixtureNotice } from "@/components/fixture-notice";
import { ArrowIcon } from "@/components/icons";
import { Reveal } from "@/components/reveal";
import { getJournalArticle, journalArticles } from "@/content/public-pages";
import { localize, siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { publicMetadata } from "@/lib/seo";

type JournalArticlePageProps = {
  params: Promise<{ locale: string; slug: string }>;
};

export function generateStaticParams() {
  return routing.locales.flatMap((locale) =>
    journalArticles.map((article) => ({ locale, slug: article.slug })),
  );
}

export async function generateMetadata({ params }: JournalArticlePageProps): Promise<Metadata> {
  const { locale, slug } = await params;
  const article = getJournalArticle(slug);
  if (!article || !hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;

  return publicMetadata({
    description: localize(article.excerpt, currentLocale),
    locale: currentLocale,
    path: `/journal/${article.slug}`,
    title: localize(article.title, currentLocale),
  });
}

export default async function JournalArticlePage({ params }: JournalArticlePageProps) {
  const { locale: localeParam, slug } = await params;
  const article = getJournalArticle(slug);
  if (!article || !hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const copy = siteCopy[locale];
  const relatedArticles = journalArticles
    .filter((entry) => entry.slug !== article.slug)
    .slice(0, 2);

  return (
    <main className="journal-article">
      <header className="journal-article__header section-shell">
        <Link className="back-link" href="/journal">
          <ArrowIcon className="directional-icon directional-icon--back" />
          {locale === "fa" ? "بازگشت به یادداشت‌ها" : "Back to journal"}
        </Link>
        <p>
          {localize(article.category, locale)} <span aria-hidden="true">·</span>{" "}
          {localize(article.readingTime, locale)}
        </p>
        <h1>{localize(article.title, locale)}</h1>
        <p>{localize(article.excerpt, locale)}</p>
      </header>
      <div className="journal-article__cover">
        <Image
          alt={localize(article.alt, locale)}
          fill
          priority
          sizes="100vw"
          src={article.cover}
        />
      </div>
      <div className="section-shell journal-article__fixture">
        <FixtureNotice>{copy.fixture}</FixtureNotice>
      </div>
      <article className="journal-article__body section-shell">
        {article.body.map((paragraph, index) => (
          <Reveal as="div" delay={index * 0.05} key={localize(paragraph, locale)}>
            <p>{localize(paragraph, locale)}</p>
          </Reveal>
        ))}
      </article>
      <section className="journal-article__related section-shell">
        <h2>{locale === "fa" ? "ادامهٔ خواندن" : "Continue reading"}</h2>
        <div>
          {relatedArticles.map((entry) => (
            <Link href={`/journal/${entry.slug}`} key={entry.slug}>
              <span>{localize(entry.category, locale)}</span>
              <strong>{localize(entry.title, locale)}</strong>
              <ArrowIcon className="directional-icon" />
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
