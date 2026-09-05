import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { EditorialHeader } from "@/components/editorial-header";
import { FixtureNotice } from "@/components/fixture-notice";
import { Reveal } from "@/components/reveal";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { getExpertise } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type ExpertisePageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: ExpertisePageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  const title = currentLocale === "fa" ? "تخصص‌ها" : "Expertise";
  const description =
    currentLocale === "fa"
      ? "معماری، معماری داخلی و باززنده‌سازی در پیش‌نمایش توسعهٔ ولوما."
      : "Architecture, interior architecture, and adaptive reuse in the VOLUMA development preview.";

  return publicMetadata({ description, locale: currentLocale, path: "/expertise", title });
}

export default async function ExpertisePage({ params }: ExpertisePageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const copy = siteCopy[locale];
  const expertise = await getExpertise(locale);

  return (
    <main className="editorial-page section-shell">
      <EditorialHeader
        eyebrow={locale === "fa" ? "تخصص‌ها" : "Expertise"}
        intro={
          locale === "fa"
            ? "حوزه‌هایی که در آن‌ها کیفیت فضا، مصالح و زمان را در یک تصمیم پیوسته می‌بینیم."
            : "Disciplines where atmosphere, material, and time are considered as one continuous decision."
        }
        title={
          locale === "fa" ? "فضاهایی برای زندگیِ دقیق‌تر." : "Places for a more attentive life."
        }
      />
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      <section
        aria-label={locale === "fa" ? "فهرست تخصص‌ها" : "Expertise list"}
        className="expertise-list"
      >
        {expertise.map((entry, index) => (
          <Reveal as="div" className="expertise-list__entry" delay={index * 0.05} key={entry.title}>
            <p>{String(entry.display_order).padStart(2, "0")}</p>
            <div>
              <h2>{entry.title}</h2>
              <p>{entry.summary}</p>
            </div>
            <div className="expertise-list__media">
              <Image
                alt=""
                fill
                priority={index === 0}
                sizes="(max-width: 767px) 100vw, 30vw"
                src={index % 2 === 0 ? "/media/courtyard-house.png" : "/media/material-shadow.png"}
              />
            </div>
          </Reveal>
        ))}
      </section>
    </main>
  );
}
