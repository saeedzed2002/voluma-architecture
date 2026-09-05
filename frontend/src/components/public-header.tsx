"use client";

import { useEffect, useRef, useState } from "react";

import { navItems, siteCopy } from "@/content/site";
import { Link, usePathname } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { alternateLocale } from "@/lib/locale";

import { CloseIcon } from "./icons";
import { ThemeControl } from "./theme-control";

type PublicHeaderProps = {
  locale: Locale;
};

export function PublicHeader({ locale }: PublicHeaderProps) {
  const copy = siteCopy[locale];
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const firstLinkRef = useRef<HTMLAnchorElement>(null);
  const otherLocale = alternateLocale(locale);

  useEffect(() => {
    if (!menuOpen) return;

    const previous = document.activeElement as HTMLElement | null;
    const trigger = triggerRef.current;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };

    document.addEventListener("keydown", onKeyDown);
    document.body.dataset.menuOpen = "true";
    firstLinkRef.current?.focus({ preventScroll: true });

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      delete document.body.dataset.menuOpen;
      (previous ?? trigger)?.focus();
    };
  }, [menuOpen]);

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link aria-label="VOLUMA home" className="wordmark" href="/">
          VOLUMA
        </Link>

        <nav aria-label={locale === "fa" ? "پیمایش اصلی" : "Primary"} className="desktop-nav">
          {navItems.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                aria-current={active ? "page" : undefined}
                href={item.href}
                key={item.href}
                prefetch={item.href === "/projects"}
              >
                {item.label[locale]}
              </Link>
            );
          })}
        </nav>

        <div className="site-header__controls">
          <button
            aria-controls="mobile-navigation"
            aria-expanded={menuOpen}
            className="menu-trigger"
            onClick={() => setMenuOpen((current) => !current)}
            ref={triggerRef}
            type="button"
          >
            {menuOpen ? <CloseIcon className="control-icon" /> : copy.menu}
            <span className="sr-only">{menuOpen ? copy.closeMenu : ""}</span>
          </button>
          <Link
            aria-label={copy.switchLocale}
            className="locale-control"
            href={pathname}
            locale={otherLocale}
          >
            <span className={locale === "en" ? "is-active" : undefined}>EN</span>
            <span aria-hidden="true">/</span>
            <span className={locale === "fa" ? "is-active" : undefined}>FA</span>
          </Link>
          <ThemeControl labels={copy.theme} />
        </div>
      </div>

      <nav
        aria-label={locale === "fa" ? "پیمایش موبایل" : "Mobile"}
        className="mobile-nav"
        data-open={menuOpen}
        id="mobile-navigation"
      >
        <div className="mobile-nav__inner">
          {navItems.map((item, index) => (
            <Link
              aria-current={pathname === item.href ? "page" : undefined}
              href={item.href}
              key={item.href}
              onClick={() => setMenuOpen(false)}
              prefetch={item.href === "/projects"}
              ref={index === 0 ? firstLinkRef : undefined}
              tabIndex={menuOpen ? 0 : -1}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              {item.label[locale]}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
