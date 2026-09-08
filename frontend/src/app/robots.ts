import type { MetadataRoute } from "next";

import { siteOrigin } from "@/lib/seo";

// `VOLUMA_PUBLIC_ORIGIN` is deployment configuration, so evaluate this
// metadata route per request instead of baking the development fallback into
// the standalone production build.
export const dynamic = "force-dynamic";

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
