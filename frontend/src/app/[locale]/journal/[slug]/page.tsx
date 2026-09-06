import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { FixtureNotice } from "@/components/fixture-notice";
import { ArrowIcon } from "@/components/icons";
import { Reveal } from "@/components/reveal";
import { siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { getArticle, getJournal, PublicApiError } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type JournalArticlePageProps = {
  params: Promise<{ locale: string; slug: string }>;
};

export async function generateMetadata({ params }: JournalArticlePageProps): Promise<Metadata> {
  const { locale, slug } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  try {
    const article = await getArticle(currentLocale, slug);
    return publicMetadata({
      description: article.seo_description,
      locale: currentLocale,
      path: `/journal/${article.slug}`,
      title: article.seo_title,
    });
  } catch (error) {
    if (error instanceof PublicApiError && error.status === 404) return {};
    throw error;
  }
}

export default async function JournalArticlePage({ params }: JournalArticlePageProps) {
  const { locale: localeParam, slug } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  let article;
  try {
    article = await getArticle(locale, slug);
  } catch (error) {
    if (error instanceof PublicApiError && error.status === 404) notFound();
    throw error;
  }
  const journal = await getJournal(locale);
  const relatedArticles = journal.items.filter((entry) => entry.slug !== article.slug).slice(0, 2);
  const copy = siteCopy[locale];

  return (
    <main className="journal-article">
      <header className="journal-article__header section-shell">
        <Link className="back-link" href="/journal">
          <ArrowIcon className="directional-icon directional-icon--back" />
          {locale === "fa" ? "بازگشت به یادداشت‌ها" : "Back to journal"}
        </Link>
        <p>
          {article.category.title} <span aria-hidden="true">·</span> {article.reading_minutes}{" "}
          {locale === "fa" ? "دقیقه مطالعه" : "min read"}
        </p>
        <h1>{article.title}</h1>
        <p>{article.excerpt}</p>
      </header>
      <div className="journal-article__cover">
        {article.cover_image ? (
          <Image alt={article.cover_image.alt} fill priority sizes="100vw" src={article.cover_image.url} />
        ) : null}
      </div>
      <div className="section-shell journal-article__fixture">
        <FixtureNotice>{copy.fixture}</FixtureNotice>
      </div>
      <article className="journal-article__body section-shell">
        {article.blocks.length > 0
          ? article.blocks.map((block, index) =>
              block.block_type === "text" ? (
                <Reveal as="div" delay={index * 0.05} key={`${block.block_type}-${index}`}>
                  {block.heading ? <h2>{block.heading}</h2> : null}
                  {block.body.split(/\n{2,}/).map((paragraph) => (
                    <p key={paragraph}>{paragraph}</p>
                  ))}
                </Reveal>
              ) : (
                <Reveal as="div" delay={index * 0.05} key={`${block.block_type}-${index}`}>
                  <blockquote>
                    <p>{block.quote}</p>
                    {block.attribution ? <footer>{block.attribution}</footer> : null}
                  </blockquote>
                </Reveal>
              ),
            )
          : article.body.map((paragraph, index) => (
              <Reveal as="div" delay={index * 0.05} key={paragraph}>
                <p>{paragraph}</p>
              </Reveal>
            ))}
      </article>
      <section className="journal-article__related section-shell">
        <h2>{locale === "fa" ? "ادامهٔ خواندن" : "Continue reading"}</h2>
        <div>
          {relatedArticles.map((entry) => (
            <Link href={`/journal/${entry.slug}`} key={entry.slug}>
              <span>{entry.category.title}</span>
              <strong>{entry.title}</strong>
              <ArrowIcon className="directional-icon" />
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
