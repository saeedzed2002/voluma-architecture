import type { MetadataRoute } from "next";

import { siteOrigin } from "@/lib/seo";

export default function robots(): MetadataRoute.Robots {
  return {
    host: siteOrigin.origin,
    rules: {
      disallow: ["/admin", "/api", "/media/originals", "/media/staging"],
      userAgent: "*",
    },
    sitemap: new URL("/sitemap.xml", siteOrigin).toString(),
  };
}
