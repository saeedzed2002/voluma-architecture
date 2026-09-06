import type { Metadata } from "next";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { ContactForm } from "@/components/contact-form";
import { EditorialHeader } from "@/components/editorial-header";
import { FixtureNotice } from "@/components/fixture-notice";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { getSite } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type ContactPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: ContactPageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  const title = currentLocale === "fa" ? "تماس" : "Contact";
  const description =
    currentLocale === "fa"
      ? "برای آغاز یک گفت‌وگو دربارهٔ مکان یا پرسش شما."
      : "Start a conversation about a place or a question.";

  return publicMetadata({ description, locale: currentLocale, path: "/contact", title });
}

export default async function ContactPage({ params }: ContactPageProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();
  const locale = localeParam as Locale;
  const copy = siteCopy[locale];
  const site = await getSite(locale);

  return (
    <main className="editorial-page section-shell contact-page">
      <EditorialHeader
        eyebrow={locale === "fa" ? "تماس" : "Contact"}
        intro={
          locale === "fa"
            ? "با یک مکان، یک پرسش یا یک امکان آغاز کنیم."
            : "Begin with a place, a question, or a possibility."
        }
        title={locale === "fa" ? "گفت‌وگویی برای شروع." : "A conversation to begin."}
      />
      <FixtureNotice>{copy.fixture}</FixtureNotice>
      {site.contact_email || site.contact_phone || site.contact_address ? (
        <aside className="contact-details" aria-label={locale === "fa" ? "اطلاعات تماس" : "Contact details"}>
          {site.contact_email ? <a href={`mailto:${site.contact_email}`}>{site.contact_email}</a> : null}
          {site.contact_phone ? <a href={`tel:${site.contact_phone}`}>{site.contact_phone}</a> : null}
          {site.contact_address ? <p>{site.contact_address}</p> : null}
        </aside>
      ) : null}
      <ContactForm locale={locale} />
    </main>
  );
}
