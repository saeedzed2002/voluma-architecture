import type { Metadata } from "next";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { HomePage } from "@/components/home-page";
import { siteCopy } from "@/content/site";
import { routing, type Locale } from "@/i18n/routing";
import { publicMetadata } from "@/lib/seo";

type PageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;

  return publicMetadata({
    description: siteCopy[currentLocale].heroBody,
    locale: currentLocale,
    path: "",
    title: siteCopy[currentLocale].descriptor,
  });
}

export default async function Page({ params }: PageProps) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();

  return <HomePage locale={locale as Locale} />;
}
