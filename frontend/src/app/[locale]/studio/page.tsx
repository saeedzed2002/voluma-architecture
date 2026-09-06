import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { EditorialHeader } from "@/components/editorial-header";
import { FixtureNotice } from "@/components/fixture-notice";
import { Reveal } from "@/components/reveal";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { getStudio } from "@/lib/public-api";
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
  const copy = siteCopy[locale];
  const studio = await getStudio(locale);

  return (
    <main className="editorial-page section-shell">
      <EditorialHeader
        eyebrow={locale === "fa" ? "استودیو" : "Studio"}
        intro={studio.intro}
        title={
          locale === "fa" ? "ممارستی بر پایهٔ نگاه دقیق." : "A practice built around attentive looking."
        }
      />
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
          {studio.principles.map((principle, index) => (
            <Reveal delay={index * 0.06} key={principle.title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h2>{principle.title}</h2>
              <p>{principle.body}</p>
            </Reveal>
          ))}
        </div>
      </section>
      <section className="studio-records" aria-labelledby="studio-records-title">
        <div className="studio-records__intro">
          <h2 id="studio-records-title">
            {locale === "fa" ? "اطلاعاتی که با تأیید منتشر می‌شوند." : "Records published with approval."}
          </h2>
          <p>
            {studio.members.length || studio.recognitions.length
              ? locale === "fa"
                ? "اطلاعات تأییدشدهٔ استودیو در این صفحه منتشر شده است."
                : "Approved studio information is published on this page."
              : locale === "fa"
                ? "افراد، همکاران و تقدیرها تا تأیید مالک منتشر نمی‌شوند."
                : "People, collaborators, and recognition remain unpublished until owner approval."}
          </p>
        </div>
        {studio.members.length || studio.recognitions.length ? (
          <div className="studio-records__content">
            {studio.members.length ? (
              <section className="studio-records__group" aria-labelledby="studio-people-title">
                <h3 id="studio-people-title">{locale === "fa" ? "افراد" : "People"}</h3>
                <ol className="studio-records__list">
                  {studio.members.map((member) => (
                    <li key={member.name}>
                      <h4>{member.name}</h4>
                      <p className="studio-records__role">{member.role}</p>
                      {member.biography ? <p>{member.biography}</p> : null}
                    </li>
                  ))}
                </ol>
              </section>
            ) : null}
            {studio.recognitions.length ? (
              <section className="studio-records__group" aria-labelledby="studio-recognition-title">
                <h3 id="studio-recognition-title">{locale === "fa" ? "تقدیرها" : "Recognition"}</h3>
                <ol className="studio-records__list studio-records__list--recognition">
                  {studio.recognitions.map((recognition) => (
                    <li key={recognition}>{recognition}</li>
                  ))}
                </ol>
              </section>
            ) : null}
          </div>
        ) : null}
      </section>
    </main>
  );
}
