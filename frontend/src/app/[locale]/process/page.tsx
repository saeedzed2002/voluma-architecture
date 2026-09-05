import type { Metadata } from "next";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { EditorialHeader } from "@/components/editorial-header";
import { FixtureNotice } from "@/components/fixture-notice";
import { Reveal } from "@/components/reveal";
import { processSteps } from "@/content/public-pages";
import { localize, siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { publicMetadata } from "@/lib/seo";

type ProcessPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: ProcessPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  const title = currentLocale === "fa" ? "فرایند" : "Process";
  const description =
    currentLocale === "fa"
      ? "فرایند طراحی ولوما، از شناخت تا تحویل."
      : "The VOLUMA design process, from discovery to delivery.";

  return publicMetadata({ description, locale: currentLocale, path: "/process", title });
}

export default async function ProcessPage({ params }: ProcessPageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const copy = siteCopy[locale];

  return (
    <main className="editorial-page section-shell">
      <EditorialHeader
        eyebrow={locale === "fa" ? "فرایند" : "Process"}
        intro={
          locale === "fa"
            ? "یک فرایند روشن، اما هرگز از پیش‌تعیین‌شده؛ برای آنکه تصمیم‌ها از مکان و مسئلهٔ واقعی آغاز شوند."
            : "A clear but never pre-scripted process, so decisions begin with the actual place and question."
        }
        title={locale === "fa" ? "از پرسش تا فضای ساخته‌شده." : "From question to built space."}
      />
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      <ol className="process-list">
        {processSteps.map((step, index) => (
          <Reveal as="li" className="process-list__step" delay={index * 0.05} key={step.index}>
            <span>{step.index}</span>
            <div>
              <h2>{localize(step.title, locale)}</h2>
              <p>{localize(step.summary, locale)}</p>
            </div>
          </Reveal>
        ))}
      </ol>
    </main>
  );
}
