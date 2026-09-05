import type { Metadata } from "next";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { FixtureNotice } from "@/components/fixture-notice";
import { privacyCopy } from "@/content/public-pages";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { publicMetadata } from "@/lib/seo";

type PrivacyPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: PrivacyPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  const title = currentLocale === "fa" ? "حریم خصوصی" : "Privacy";
  const description =
    currentLocale === "fa"
      ? "اطلاعات روشن دربارهٔ داده‌های فرم تماس در پیش‌نمایش ولوما."
      : "Plain-language contact-form data information for the VOLUMA preview.";

  return publicMetadata({ description, locale: currentLocale, path: "/privacy", title });
}

export default async function PrivacyPage({ params }: PrivacyPageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const content = privacyCopy[locale];
  const copy = siteCopy[locale];

  return (
    <main className="privacy-page section-shell">
      <header className="privacy-page__header">
        <p>{locale === "fa" ? "حریم خصوصی" : "Privacy"}</p>
        <h1>{content.title}</h1>
        <p>{content.intro}</p>
      </header>
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      <div className="privacy-page__sections">
        {content.sections.map(([title, body], index) => (
          <section key={title}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <div>
              <h2>{title}</h2>
              <p>{body}</p>
            </div>
          </section>
        ))}
      </div>
    </main>
  );
}
