import Image from "next/image";

import { projects, siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";

import { ArrowIcon } from "./icons";
import { FixtureNotice } from "./fixture-notice";
import { ProjectLink } from "./project-link";
import { Reveal } from "./reveal";

type HomePageProps = {
  locale: Locale;
};

export function HomePage({ locale }: HomePageProps) {
  const copy = siteCopy[locale];

  return (
    <main>
      <section className="home-hero">
        <Reveal className="home-hero__copy">
          <h1>{copy.heroTitle}</h1>
          <p>{copy.heroBody}</p>
          <Link className="text-link" href="/projects">
            {copy.heroCta}
            <ArrowIcon className="directional-icon" />
          </Link>
        </Reveal>
        <div className="home-hero__media">
          <Image
            alt={
              locale === "fa"
                ? "خانه‌ی بتنی و چوبی رو به کوهستان و دریاچه"
                : "Concrete and timber house overlooking mountains and a lake"
            }
            fill
            priority
            sizes="(max-width: 767px) 100vw, 58vw"
            src="/media/voluma-mountain-house.png"
          />
        </div>
      </section>

      <section className="selected-projects section-shell" id="selected-work">
        <Reveal>
          <h2 className="section-title">{copy.selectedProjects}</h2>
        </Reveal>
        <div className="selected-projects__grid">
          <Reveal>
            <ProjectLink locale={locale} priority project={projects[0]} variant="feature" />
          </Reveal>
          <Reveal delay={0.08}>
            <ProjectLink locale={locale} project={projects[1]} variant="feature" />
          </Reveal>
        </div>
      </section>

      <section className="studio-statement">
        <Reveal className="studio-statement__copy section-shell--inset">
          <h2>{copy.statementTitle}</h2>
          <div>
            <p>{copy.statementBody}</p>
            <Link className="text-link" href="/studio">
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
            {copy.expertise.map((item, index) => (
              <li key={item}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{item}</strong>
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
          <Reveal className="featured-story__copy">
            <p>{copy.storyLabel}</p>
            <h2>{copy.storyTitle}</h2>
            <Link
              aria-label={copy.storyTitle}
              className="icon-link"
              href="/journal/material-as-memory"
            >
              <ArrowIcon className="directional-icon" />
            </Link>
          </Reveal>
          <Reveal className="featured-story__media" delay={0.08}>
            <Image
              alt={
                locale === "fa"
                  ? "سایه‌ی برگ‌ها روی سطح بتن و چوب"
                  : "Leaf shadows across concrete and oak surfaces"
              }
              fill
              sizes="(max-width: 767px) 100vw, 58vw"
              src="/media/material-shadow.png"
            />
          </Reveal>
        </section>

        <section className="process section-shell">
          <Reveal>
            <h2>{copy.processTitle}</h2>
          </Reveal>
          <ol>
            {copy.process.map((step, index) => (
              <Reveal as="li" delay={index * 0.05} key={step}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{step}</strong>
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
          {copy.journal.map((item, index) => (
            <Reveal delay={index * 0.06} key={item.title}>
              <article className="journal-row">
                <div className="journal-row__media">
                  <Image
                    alt=""
                    fill
                    sizes="(max-width: 767px) 100vw, 45vw"
                    src={index === 0 ? "/media/material-shadow.png" : "/media/courtyard-house.png"}
                  />
                </div>
                <div className="journal-row__copy">
                  <div>
                    <h3>{item.title}</h3>
                    <p>{item.meta}</p>
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
          <Link className="text-link text-link--inverse" href="/contact">
            {copy.cta}
            <ArrowIcon className="directional-icon" />
          </Link>
        </Reveal>
      </section>
    </main>
  );
}
