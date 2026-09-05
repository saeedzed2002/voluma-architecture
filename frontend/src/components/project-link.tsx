import Image from "next/image";

import type { Project } from "@/content/site";
import { localize } from "@/content/site";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { formatYear } from "@/lib/locale";

import { ArrowIcon } from "./icons";

type ProjectLinkProps = {
  locale: Locale;
  project: Project;
  priority?: boolean;
  variant?: "feature" | "archive" | "related";
};

export function ProjectLink({
  locale,
  project,
  priority = false,
  variant = "archive",
}: ProjectLinkProps) {
  return (
    <article className="project-link" data-variant={variant}>
      <Link aria-label={localize(project.title, locale)} href={`/projects/${project.slug}`}>
        <div className="project-link__media">
          <Image
            alt={localize(project.alt, locale)}
            fill
            priority={priority}
            sizes={
              variant === "feature"
                ? "(max-width: 767px) 100vw, 58vw"
                : "(max-width: 767px) 100vw, (max-width: 1199px) 50vw, 34vw"
            }
            src={project.image}
            style={{ objectPosition: project.imagePosition ?? "center" }}
          />
        </div>
        <div className="project-link__meta">
          <div>
            <h3>{localize(project.title, locale)}</h3>
            <p>
              {localize(project.categoryLabel, locale)} <span aria-hidden="true">·</span>{" "}
              {formatYear(project.year, locale)}
              {variant === "archive" ? (
                <>
                  {" "}
                  <span aria-hidden="true">·</span> {localize(project.location, locale)}
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
