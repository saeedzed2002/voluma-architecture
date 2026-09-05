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

  return {
    title: { default: t("title"), template: `%s — ${t("title")}` },
    description: t("description"),
  };
}

export default async function LocaleLayout({ children, params }: LocaleLayoutProps) {
  const { locale: localeParam } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();

  const locale = localeParam as Locale;
  const direction = directionForLocale(locale);
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
        <Script
          dangerouslySetInnerHTML={{ __html: themeInitScript }}
          id="voluma-theme-init"
          strategy="beforeInteractive"
        />
        <NextIntlClientProvider>
          <a className="skip-link" href="#main-content">
            {locale === "fa" ? "رفتن به محتوای اصلی" : "Skip to main content"}
          </a>
          <PublicHeader locale={locale} />
          <div id="main-content" tabIndex={-1}>
            {children}
          </div>
          <PublicFooter locale={locale} />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
