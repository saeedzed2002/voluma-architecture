import { navItems, siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import type { PublicSite } from "@/lib/public-api";

type PublicFooterProps = {
  locale: Locale;
  site: PublicSite;
};

export function PublicFooter({ locale, site }: PublicFooterProps) {
  const copy = siteCopy[locale];
  const copyright = `© ${new Date().getFullYear()} ${site.studio_name}`;

  return (
    <footer className="site-footer">
      <div className="site-footer__grid">
        <div className="site-footer__identity">
          <Link className="wordmark wordmark--footer" href="/">
            {site.studio_name}
          </Link>
          <p>{copy.descriptor}</p>
        </div>
        <nav
          aria-label={locale === "fa" ? "پیوندهای پایین صفحه" : "Footer"}
          className="site-footer__nav"
        >
          {navItems.map((item) => (
            <Link href={item.href} key={item.href} prefetch={item.href === "/projects"}>
              {item.label[locale]}
            </Link>
          ))}
          <Link href="/privacy" prefetch={false}>
            {copy.privacy}
          </Link>
          {site.contact_email ? <a href={`mailto:${site.contact_email}`}>{site.contact_email}</a> : null}
          {site.contact_phone ? <a href={`tel:${site.contact_phone}`}>{site.contact_phone}</a> : null}
          {site.social_links.map((link) => (
            <a href={link.url} key={link.url} rel="noreferrer" target="_blank">
              {link.label}
            </a>
          ))}
        </nav>
      </div>
      <div className="site-footer__base">
        {site.contact_address ? <span>{site.contact_address}</span> : <span />}
        <span>{copyright}</span>
      </div>
    </footer>
  );
}
