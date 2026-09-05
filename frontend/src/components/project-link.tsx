import Image from "next/image";

import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { formatYear } from "@/lib/locale";
import type { PublicProject } from "@/lib/public-api";

import { ArrowIcon } from "./icons";

type ProjectLinkProps = {
  locale: Locale;
  project: PublicProject;
  priority?: boolean;
  variant?: "feature" | "archive" | "related";
};

export function ProjectLink({
  locale,
  project,
  priority = false,
  variant = "archive",
}: ProjectLinkProps) {
  const typology = project.typologies[0]?.title ?? (locale === "fa" ? "پروژه" : "Project");
  const coverImage = project.cover_image;

  return (
    <article className="project-link" data-variant={variant}>
      <Link aria-label={project.title} href={`/projects/${project.slug}`}>
        <div className="project-link__media">
          {coverImage ? (
            <Image
              alt={coverImage.alt}
              fill
              priority={priority}
              sizes={
                variant === "feature"
                  ? "(max-width: 767px) 100vw, 58vw"
                  : "(max-width: 767px) 100vw, (max-width: 1199px) 50vw, 34vw"
              }
              src={coverImage.url}
            />
          ) : null}
        </div>
        <div className="project-link__meta">
          <div>
            <h3>{project.title}</h3>
            <p>
              {typology} <span aria-hidden="true">·</span>{" "}
              {project.completion_year ? formatYear(String(project.completion_year), locale) : "—"}
              {variant === "archive" ? (
                <>
                  <span aria-hidden="true">·</span> {project.location}
                </>
              ) : null}
            </p>
          </div>
          <ArrowIcon className="directional-icon project-link__arrow" />
        </div>
      </Link>
    </article>
  );
}
