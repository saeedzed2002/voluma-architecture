import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { FixtureNotice } from "@/components/fixture-notice";
import { ArrowIcon } from "@/components/icons";
import { ProjectGallery, type GalleryImage } from "@/components/project-gallery";
import { ProjectLink } from "@/components/project-link";
import { Reveal } from "@/components/reveal";
import { siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { formatYear } from "@/lib/locale";
import { getProject, getProjects, PublicApiError } from "@/lib/public-api";
import { publicMetadata } from "@/lib/seo";

type ProjectPageProps = {
  params: Promise<{ locale: string; slug: string }>;
};

export async function generateMetadata({ params }: ProjectPageProps): Promise<Metadata> {
  const { locale, slug } = await params;
  if (!hasLocale(routing.locales, locale)) return {};
  const currentLocale = locale as Locale;
  try {
    const project = await getProject(currentLocale, slug);
    return publicMetadata({
      description: project.summary,
      locale: currentLocale,
      path: `/projects/${project.slug}`,
      title: project.title,
    });
  } catch (error) {
    if (error instanceof PublicApiError && error.status === 404) return {};
    throw error;
  }
}

export default async function ProjectPage({ params }: ProjectPageProps) {
  const { locale: localeParam, slug } = await params;
  if (!hasLocale(routing.locales, localeParam)) notFound();

  const locale = localeParam as Locale;
  let project;
  try {
    project = await getProject(locale, slug);
  } catch (error) {
    if (error instanceof PublicApiError && error.status === 404) notFound();
    throw error;
  }
  const archive = await getProjects(locale);
  const copy = siteCopy[locale];
  const projectIndex = archive.items.findIndex((entry) => entry.slug === slug);
  const previous = archive.items[(projectIndex - 1 + archive.items.length) % archive.items.length];
  const next = archive.items[(projectIndex + 1) % archive.items.length];
  const related = archive.items.filter((entry) => entry.slug !== slug).slice(0, 2);
  const galleryImages: GalleryImage[] = project.gallery.map((image, index) => ({
    src: image.url,
    alt: image.alt,
    caption: index === 0 ? copy.detailCaption : copy.materialCaption,
  }));

  return (
    <main className="project-page">
      <header className="project-hero section-shell">
        <Link className="back-link" href="/projects">
          <ArrowIcon className="directional-icon directional-icon--back" />
          {copy.backToProjects}
        </Link>
        <div className="project-hero__heading">
          <h1>{project.title}</h1>
          <p>{project.summary}</p>
        </div>
      </header>

      <div className="project-hero__media">
        {project.cover_image ? (
          <Image alt={project.cover_image.alt} fill priority sizes="100vw" src={project.cover_image.url} />
        ) : null}
      </div>

      <div className="project-fixture section-shell">
        <FixtureNotice>{copy.fixture}</FixtureNotice>
      </div>

      <dl className="project-facts section-shell">
        {[
          [copy.facts.type, project.typologies.map((typology) => typology.title).join(" · ")],
          [copy.facts.location, project.location],
          [copy.facts.status, project.status],
          [
            copy.facts.year,
            project.completion_year ? formatYear(String(project.completion_year), locale) : null,
          ],
          [copy.facts.area, project.area],
          [copy.facts.scope, project.scope],
        ]
          .filter(([, value]) => value)
          .map(([term, value]) => (
            <div key={term}>
              <dt>{term}</dt>
              <dd>{value}</dd>
            </div>
          ))}
      </dl>

      {project.introduction ? (
        <section className="project-intro section-shell">
          <Reveal>
            <h2>{project.introduction.title}</h2>
            <p>{project.introduction.body}</p>
          </Reveal>
          <Reveal className="project-intro__drawing" delay={0.08}>
            {project.cover_image ? (
              <Image
                alt={project.cover_image.alt}
                fill
                sizes="(max-width: 767px) 100vw, 44vw"
                src={project.cover_image.url}
              />
            ) : null}
          </Reveal>
        </section>
      ) : null}

      {project.narrative ? (
        <section className="project-narrative section-shell">
          <Reveal className="project-narrative__copy">
            <h2>{project.narrative.title}</h2>
            <p>{project.narrative.body}</p>
            <small>{copy.detailCaption}</small>
          </Reveal>
          <Reveal className="project-narrative__media" delay={0.08}>
            {project.cover_image ? (
              <Image
                alt={project.cover_image.alt}
                fill
                sizes="(max-width: 767px) 100vw, 58vw"
                src={project.cover_image.url}
              />
            ) : null}
          </Reveal>
        </section>
      ) : null}

      {project.quote ? (
        <Reveal className="project-quote section-shell">
          <blockquote>“{project.quote}”</blockquote>
        </Reveal>
      ) : null}

      {project.material ? (
        <section className="project-material section-shell">
          <Reveal className="project-material__copy">
            <h2>{project.material.title}</h2>
            <p>{project.material.body}</p>
          </Reveal>
          {galleryImages.length ? (
            <ProjectGallery
              closeLabel={copy.closeGallery}
              images={galleryImages}
              locale={locale}
              nextLabel={locale === "fa" ? "تصویر بعدی" : "Next image"}
              openLabel={copy.openImage}
              previousLabel={locale === "fa" ? "تصویر قبلی" : "Previous image"}
            />
          ) : null}
        </section>
      ) : null}

      <section className="related-projects section-shell">
        <h2 className="section-title">{copy.continueExploring}</h2>
        <div className="related-projects__grid">
          {related.map((entry) => (
            <ProjectLink key={entry.slug} locale={locale} project={entry} variant="related" />
          ))}
        </div>
        {previous && next ? (
          <nav
            aria-label={locale === "fa" ? "پیمایش پروژه‌ها" : "Project navigation"}
            className="project-pagination"
          >
            <Link href={`/projects/${previous.slug}`}>
              <ArrowIcon className="directional-icon directional-icon--back" />
              <span>
                <small>{copy.previousProject}</small>
                {previous.title}
              </span>
            </Link>
            <Link href={`/projects/${next.slug}`}>
              <span>
                <small>{copy.nextProject}</small>
                {next.title}
              </span>
              <ArrowIcon className="directional-icon" />
            </Link>
          </nav>
        ) : null}
      </section>
    </main>
  );
}
