import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { EditorialHeader } from "@/components/editorial-header";
import { FixtureNotice } from "@/components/fixture-notice";
import { Reveal } from "@/components/reveal";
import { studioCopy } from "@/content/public-pages";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { publicMetadata } from "@/lib/seo";

type StudioPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: StudioPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  const title = currentLocale === "fa" ? "استودیو" : "Studio";
  const description =
    currentLocale === "fa"
      ? "رویکرد و فلسفهٔ استودیوی ولوما در پیش‌نمایش توسعه."
      : "The VOLUMA studio approach and philosophy in the development preview.";

  return publicMetadata({ description, locale: currentLocale, path: "/studio", title });
}

export default async function StudioPage({ params }: StudioPageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const content = studioCopy[locale];
  const copy = siteCopy[locale];

  return (
    <main className="editorial-page section-shell">
      <EditorialHeader eyebrow={content.eyebrow} intro={content.intro} title={content.title} />
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      <section className="studio-philosophy">
        <Reveal className="studio-philosophy__media">
          <Image
            alt={
              locale === "fa"
                ? "نور و سایه در آستانهٔ یک خانهٔ حیاط‌دار"
                : "Light and shade at the threshold of a courtyard house"
            }
            fill
            priority
            sizes="(max-width: 767px) 100vw, 48vw"
            src="/media/courtyard-house.png"
          />
        </Reveal>
        <div className="studio-philosophy__principles">
          {content.principles.map(([title, body], index) => (
            <Reveal delay={index * 0.06} key={title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h2>{title}</h2>
              <p>{body}</p>
            </Reveal>
          ))}
        </div>
      </section>
      <section className="studio-records">
        <h2>{content.recordsTitle}</h2>
        <p>{content.recordsBody}</p>
      </section>
    </main>
  );
}
