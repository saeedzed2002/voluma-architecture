import type { Metadata } from "next";

import type { Locale } from "@/i18n/routing";
import { getSite } from "@/lib/public-api";

const fallbackOrigin = "http://localhost:3000";

export const siteOrigin = new URL(process.env.VOLUMA_PUBLIC_ORIGIN ?? fallbackOrigin);

type PageMetadataInput = {
  description: string;
  locale: Locale;
  path: string;
  title: string;
};

function localizedPath(locale: Locale, path: string) {
  return `/${locale}${path}`;
}

export async function publicMetadata({
  description,
  locale,
  path,
  title,
}: PageMetadataInput): Promise<Metadata> {
  const site = await getSite(locale);
  const canonical = localizedPath(locale, path);

  return {
    alternates: {
      canonical,
      languages: {
        en: localizedPath("en", path),
        fa: localizedPath("fa", path),
        "x-default": localizedPath("en", path),
      },
    },
    description,
    openGraph: {
      description,
      locale: locale === "fa" ? "fa_IR" : "en_US",
      siteName: site.studio_name,
      title,
      type: "website",
      url: canonical,
    },
    title,
    twitter: {
      card: "summary_large_image",
      description,
      title,
    },
  };
}
