import type { Metadata } from "next";
import Script from "next/script";
import { hasLocale, NextIntlClientProvider } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";

import { PublicFooter } from "@/components/public-footer";
import { PublicHeader } from "@/components/public-header";
import { routing, type Locale } from "@/i18n/routing";
import { directionForLocale } from "@/lib/locale";
import { getSite } from "@/lib/public-api";
import { siteOrigin } from "@/lib/seo";
import { themeInitScript } from "@/lib/theme";

import { instrumentSans, vazirmatn } from "../fonts";
import "../globals.css";

type LocaleLayoutProps = {
  children: ReactNode;
  params: Promise<{ locale: string }>;
};

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata({ params }: LocaleLayoutProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const t = await getTranslations({ locale, namespace: "Metadata" });
  const site = await getSite(locale as Locale);
  const title = site.seo_title ?? t("title");
  const description = site.seo_description ?? t("description");

  return {
    alternates: {
      canonical: `/${locale}`,
      languages: {
        en: "/en",
        fa: "/fa",
        "x-default": "/en",
      },
    },
    metadataBase: siteOrigin,
    title: { default: title, template: `%s — ${site.studio_name}` },
    description,
    icons: site.favicon_url ? { icon: site.favicon_url } : undefined,
    openGraph: {
      description,
      locale: locale === "fa" ? "fa_IR" : "en_US",
      siteName: site.studio_name,
      title,
      type: "website",
      url: `/${locale}`,
    },
    twitter: {
      card: "summary_large_image",
      description,
      title,
    },
  };
}

export default async function LocaleLayout({ children, params }: LocaleLayoutProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();

  const locale = localeParam as Locale;
  const direction = directionForLocale(locale);
  const site = await getSite(locale);
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        name: site.studio_name,
        url: siteOrigin.origin,
      },
      {
        "@type": "WebSite",
        inLanguage: locale === "fa" ? "fa-IR" : "en-US",
        name: site.studio_name,
        url: new URL(`/${locale}`, siteOrigin).toString(),
      },
    ],
  };
  setRequestLocale(locale);

  return (
    <html
      className={`${instrumentSans.variable} ${vazirmatn.variable}`}
      data-scroll-behavior="smooth"
      dir={direction}
      lang={locale}
      suppressHydrationWarning
    >
      <body>
        <Script id="voluma-theme-init" strategy="beforeInteractive">
          {themeInitScript(site.default_theme)}
        </Script>
        <script
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
          type="application/ld+json"
        />
        <NextIntlClientProvider>
          <a className="skip-link" href="#main-content">
            {locale === "fa" ? "رفتن به محتوای اصلی" : "Skip to main content"}
          </a>
          <PublicHeader locale={locale} studioName={site.studio_name} />
          <div id="main-content" tabIndex={-1}>
            {children}
          </div>
          <PublicFooter locale={locale} site={site} />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
