import type { Metadata } from "next";
import Image from "next/image";
import { hasLocale } from "next-intl";
import { notFound } from "next/navigation";

import { FixtureNotice } from "@/components/fixture-notice";
import { ArrowIcon } from "@/components/icons";
import { ProjectGallery, type GalleryImage } from "@/components/project-gallery";
import { ProjectLink } from "@/components/project-link";
import { Reveal } from "@/components/reveal";
import { getProject, localize, projects, siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { formatYear } from "@/lib/locale";
import { publicMetadata } from "@/lib/seo";

type ProjectPageProps = {
  params: Promise<{ locale: string; slug: string }>;
};

export function generateStaticParams() {
  return routing.locales.flatMap((locale) =>
    projects.map((project) => ({ locale, slug: project.slug })),
  );
}

export async function generateMetadata({ params }: ProjectPageProps): Promise<Metadata> {
  const { locale, slug } = await params;
  const project = getProject(slug);
  if (!project || !hasLocale(routing.locales, locale)) return {};

  const currentLocale = locale as Locale;
  return publicMetadata({
    description: project.summary[currentLocale],
    locale: currentLocale,
    path: `/projects/${project.slug}`,
    title: project.title[currentLocale],
  });
}

export default async function ProjectPage({ params }: ProjectPageProps) {
  const { locale: localeParam, slug } = await params;
  const project = getProject(slug);
  if (!project || !hasLocale(routing.locales, localeParam)) notFound();

  const locale = localeParam as Locale;
  const copy = siteCopy[locale];
  const projectIndex = projects.findIndex((entry) => entry.slug === slug);
  const previous = projects[(projectIndex - 1 + projects.length) % projects.length];
  const next = projects[(projectIndex + 1) % projects.length];
  const related = [next, projects[(projectIndex + 2) % projects.length]];
  const galleryImages: GalleryImage[] = [
    {
      src: project.image,
      alt: localize(project.alt, locale),
      caption: copy.detailCaption,
    },
    {
      src: "/media/material-shadow.png",
      alt:
        locale === "fa"
          ? "سایه‌ی برگ‌ها روی بتن و قاب بلوط"
          : "Leaf shadows on concrete and an oak frame",
      caption: copy.materialCaption,
    },
    {
      src: "/media/northline-atelier.png",
      alt:
        locale === "fa"
          ? "فضای داخلی بتنی و چوبی رو به درختان"
          : "Concrete and oak interior facing trees",
      caption: copy.interiorCaption,
    },
  ];

  return (
    <main className="project-page">
      <header className="project-hero section-shell">
        <Link className="back-link" href="/projects">
          <ArrowIcon className="directional-icon directional-icon--back" />
          {copy.backToProjects}
        </Link>
        <div className="project-hero__heading">
          <h1>{localize(project.title, locale)}</h1>
          <p>{localize(project.summary, locale)}</p>
        </div>
      </header>

      <div className="project-hero__media">
        <Image
          alt={localize(project.alt, locale)}
          fill
          priority
          sizes="100vw"
          src={project.image}
          style={{ objectPosition: project.imagePosition ?? "center" }}
        />
      </div>

      <div className="project-fixture section-shell">
        <FixtureNotice>{copy.fixture}</FixtureNotice>
      </div>

      <dl className="project-facts section-shell">
        {[
          [copy.facts.type, localize(project.categoryLabel, locale)],
          [copy.facts.location, localize(project.location, locale)],
          [copy.facts.status, localize(project.status, locale)],
          [copy.facts.year, formatYear(project.year, locale)],
          [copy.facts.area, localize(project.area, locale)],
          [copy.facts.scope, localize(project.scope, locale)],
        ].map(([term, value]) => (
          <div key={term}>
            <dt>{term}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <section className="project-intro section-shell">
        <Reveal>
          <h2>{localize(project.introTitle, locale)}</h2>
          <p>{localize(project.intro, locale)}</p>
        </Reveal>
        <Reveal className="project-intro__drawing" delay={0.08}>
          <Image
            alt={
              locale === "fa"
                ? "جزئیات اتصال بتن، چوب و شیشه"
                : "Detail of concrete, oak, and glass junctions"
            }
            fill
            sizes="(max-width: 767px) 100vw, 44vw"
            src="/media/material-shadow.png"
          />
        </Reveal>
      </section>

      <section className="project-narrative section-shell">
        <Reveal className="project-narrative__copy">
          <h2>{localize(project.narrativeTitle, locale)}</h2>
          <p>{localize(project.narrative, locale)}</p>
          <small>{copy.detailCaption}</small>
        </Reveal>
        <Reveal className="project-narrative__media" delay={0.08}>
          <Image
            alt={localize(project.alt, locale)}
            fill
            sizes="(max-width: 767px) 100vw, 58vw"
            src={project.image}
          />
        </Reveal>
      </section>

      <Reveal className="project-quote section-shell">
        <blockquote>“{localize(project.quote, locale)}”</blockquote>
      </Reveal>

      <section className="project-material section-shell">
        <Reveal className="project-material__copy">
          <h2>{localize(project.materialTitle, locale)}</h2>
          <p>{localize(project.material, locale)}</p>
        </Reveal>
        <ProjectGallery
          closeLabel={copy.closeGallery}
          images={galleryImages.slice(1)}
          locale={locale}
          nextLabel={locale === "fa" ? "تصویر بعدی" : "Next image"}
          openLabel={copy.openImage}
          previousLabel={locale === "fa" ? "تصویر قبلی" : "Previous image"}
        />
      </section>

      <section className="related-projects section-shell">
        <h2 className="section-title">{copy.continueExploring}</h2>
        <div className="related-projects__grid">
          {related.map((entry) => (
            <ProjectLink key={entry.slug} locale={locale} project={entry} variant="related" />
          ))}
        </div>
        <nav
          aria-label={locale === "fa" ? "پیمایش پروژه‌ها" : "Project navigation"}
          className="project-pagination"
        >
          <Link href={`/projects/${previous.slug}`}>
            <ArrowIcon className="directional-icon directional-icon--back" />
            <span>
              <small>{copy.previousProject}</small>
              {localize(previous.title, locale)}
            </span>
          </Link>
          <Link href={`/projects/${next.slug}`}>
            <span>
              <small>{copy.nextProject}</small>
              {localize(next.title, locale)}
            </span>
            <ArrowIcon className="directional-icon" />
          </Link>
        </nav>
      </section>
    </main>
  );
}
