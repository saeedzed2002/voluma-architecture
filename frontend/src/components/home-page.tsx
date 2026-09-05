import Image from "next/image";

import { siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { PublicHome } from "@/lib/public-api";

import { ArrowIcon } from "./icons";
import { FixtureNotice } from "./fixture-notice";
import { ProjectLink } from "./project-link";
import { Reveal } from "./reveal";

type HomePageProps = {
  home: PublicHome;
  locale: Locale;
};

export function HomePage({ home, locale }: HomePageProps) {
  const copy = siteCopy[locale];
  const featuredStory = home.journal[0];

  return (
    <main>
      <section className="home-hero">
        <Reveal className="home-hero__copy">
          <h1>{home.hero_title}</h1>
          <p>{home.hero_body}</p>
          <Link className="text-link" href="/projects">
            {copy.heroCta}
            <ArrowIcon className="directional-icon" />
          </Link>
        </Reveal>
        <div className="home-hero__media">
          {home.hero_image ? (
            <Image
              alt={home.hero_image.alt}
              fill
              priority
              sizes="(max-width: 767px) 100vw, 58vw"
              src={home.hero_image.url}
            />
          ) : null}
        </div>
      </section>

      <section className="selected-projects section-shell" id="selected-work">
        <Reveal>
          <h2 className="section-title">{copy.selectedProjects}</h2>
        </Reveal>
        <div className="selected-projects__grid">
          {home.selected_projects.map((project, index) => (
            <Reveal delay={index * 0.08} key={project.slug}>
              <ProjectLink locale={locale} priority={index === 0} project={project} variant="feature" />
            </Reveal>
          ))}
        </div>
      </section>

      <section className="studio-statement">
        <Reveal className="studio-statement__copy section-shell--inset">
          <h2>{copy.statementTitle}</h2>
          <div>
            <p>{copy.statementBody}</p>
            <Link className="text-link" href="/studio" prefetch={false}>
              {copy.statementCta}
              <ArrowIcon className="directional-icon" />
            </Link>
          </div>
        </Reveal>
        <div className="studio-statement__media">
          <Image
            alt={
              locale === "fa"
                ? "نور و سایه در آستانه‌ی یک خانه‌ی حیاط‌دار"
                : "Light and shade at the threshold of a courtyard house"
            }
            fill
            sizes="(max-width: 767px) 100vw, 42vw"
            src="/media/courtyard-house.png"
          />
        </div>
      </section>

      <section className="expertise section-shell">
        <Reveal className="expertise__index">
          <h2 className="section-title">{copy.expertiseTitle}</h2>
          <ol>
            {home.expertise.map((item, index) => (
              <li key={item.title}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{item.title}</strong>
                <ArrowIcon className="directional-icon" />
              </li>
            ))}
          </ol>
        </Reveal>
        <Reveal className="expertise__media" delay={0.08}>
          <Image
            alt={
              locale === "fa"
                ? "جزئیات بتن، قاب چوبی و شاخه‌های سبز"
                : "Concrete detail, oak frame, and green branches"
            }
            fill
            sizes="(max-width: 767px) 100vw, 40vw"
            src="/media/material-shadow.png"
          />
        </Reveal>
      </section>

      <div className="dark-editorial">
        <section className="featured-story section-shell">
          {featuredStory ? (
            <>
              <Reveal className="featured-story__copy">
                <p>{featuredStory.category.title}</p>
                <h2>{featuredStory.title}</h2>
                <Link
                  aria-label={featuredStory.title}
                  className="icon-link"
                  href={`/journal/${featuredStory.slug}`}
                  prefetch={false}
                >
                  <ArrowIcon className="directional-icon" />
                </Link>
              </Reveal>
              <Reveal className="featured-story__media" delay={0.08}>
                {featuredStory.cover_image ? (
                  <Image
                    alt={featuredStory.cover_image.alt}
                    fill
                    sizes="(max-width: 767px) 100vw, 58vw"
                    src={featuredStory.cover_image.url}
                  />
                ) : null}
              </Reveal>
            </>
          ) : null}
        </section>

        <section className="process section-shell">
          <Reveal>
            <h2>{copy.processTitle}</h2>
          </Reveal>
          <ol>
          {home.process.map((step, index) => (
            <Reveal as="li" delay={index * 0.05} key={step.title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{step.title}</strong>
                <ArrowIcon className="directional-icon" />
              </Reveal>
            ))}
          </ol>
        </section>
      </div>

      <section className="journal section-shell">
        <Reveal>
          <h2 className="section-title">{copy.journalTitle}</h2>
        </Reveal>
        <div className="journal__list">
          {home.journal.map((item, index) => (
            <Reveal delay={index * 0.06} key={item.slug}>
              <article className="journal-row">
                <div className="journal-row__media">
                  {item.cover_image ? (
                    <Image
                      alt={item.cover_image.alt}
                      fill
                      sizes="(max-width: 767px) 100vw, 45vw"
                      src={item.cover_image.url}
                    />
                  ) : null}
                </div>
                <div className="journal-row__copy">
                  <div>
                    <h3>{item.title}</h3>
                    <p>
                      {item.category.title} · {item.reading_minutes} {locale === "fa" ? "دقیقه" : "min read"}
                    </p>
                  </div>
                  <ArrowIcon className="directional-icon" />
                </div>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      <div className="section-shell fixture-wrap">
        <FixtureNotice>{copy.fixture}</FixtureNotice>
      </div>

      <section className="closing-cta">
        <Reveal className="section-shell closing-cta__inner">
          <h2>{copy.ctaTitle}</h2>
          <Link className="text-link text-link--inverse" href="/contact" prefetch={false}>
            {copy.cta}
            <ArrowIcon className="directional-icon" />
          </Link>
        </Reveal>
      </section>
    </main>
  );
}
