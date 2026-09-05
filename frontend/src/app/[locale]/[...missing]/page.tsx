import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { routing } from "@/i18n/routing";

type MissingPageProps = {
  params: Promise<{ locale: string; missing: string[] }>;
};

export default async function MissingPage({ params }: MissingPageProps) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();

  notFound();
}
