import type { MetadataRoute } from "next";

import { siteOrigin } from "@/lib/seo";
import { getAllJournalArticles, getAllProjects } from "@/lib/public-api";

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

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const localizedStaticPaths = ["en", "fa"].flatMap((locale) =>
    staticPaths.map((path) => ({ url: new URL(`/${locale}${path}`, siteOrigin).toString() })),
  );
  const [englishProjects, persianProjects, englishArticles, persianArticles] = await Promise.all([
    getAllProjects("en"),
    getAllProjects("fa"),
    getAllJournalArticles("en"),
    getAllJournalArticles("fa"),
  ]);
  const projectPaths = [
    ...englishProjects.map((project) => ({
      url: new URL(`/en/projects/${project.slug}`, siteOrigin).toString(),
    })),
    ...persianProjects.map((project) => ({
      url: new URL(`/fa/projects/${project.slug}`, siteOrigin).toString(),
    })),
  ];
  const articlePaths = [
    ...englishArticles.map((article) => ({
      url: new URL(`/en/journal/${article.slug}`, siteOrigin).toString(),
    })),
    ...persianArticles.map((article) => ({
      url: new URL(`/fa/journal/${article.slug}`, siteOrigin).toString(),
    })),
  ];

  return [...localizedStaticPaths, ...projectPaths, ...articlePaths];
}
