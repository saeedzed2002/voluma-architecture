import type { MetadataRoute } from "next";

import { journalArticles } from "@/content/public-pages";
import { projects } from "@/content/site";
import { siteOrigin } from "@/lib/seo";

const staticPaths = [
  "",
  "/projects",
  "/expertise",
  "/process",
  "/studio",
  "/journal",
  "/contact",
  "/privacy",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const localizedStaticPaths = ["en", "fa"].flatMap((locale) =>
    staticPaths.map((path) => ({ url: new URL(`/${locale}${path}`, siteOrigin).toString() })),
  );
  const projectPaths = ["en", "fa"].flatMap((locale) =>
    projects.map((project) => ({
      url: new URL(`/${locale}/projects/${project.slug}`, siteOrigin).toString(),
    })),
  );
  const articlePaths = ["en", "fa"].flatMap((locale) =>
    journalArticles.map((article) => ({
      url: new URL(`/${locale}/journal/${article.slug}`, siteOrigin).toString(),
    })),
  );

  return [...localizedStaticPaths, ...projectPaths, ...articlePaths];
}
