import type { Metadata } from "next";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { HomePage } from "@/components/home-page";
import { routing, type Locale } from "@/i18n/routing";
import { getHome } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type PageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;

  const home = await getHome(currentLocale);
  return publicMetadata({
    description: home.hero_body,
    locale: currentLocale,
    path: "",
    title: home.studio_name,
  });
}

export default async function Page({ params }: PageProps) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();

  const currentLocale = locale as Locale;
  return <HomePage home={await getHome(currentLocale)} locale={currentLocale} />;
}
