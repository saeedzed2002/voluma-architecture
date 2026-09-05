import { navItems, siteCopy } from "@/content/site";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";

type PublicFooterProps = {
  locale: Locale;
};

export function PublicFooter({ locale }: PublicFooterProps) {
  const copy = siteCopy[locale];

  return (
    <footer className="site-footer">
      <div className="site-footer__grid">
        <div className="site-footer__identity">
          <Link className="wordmark wordmark--footer" href="/">
            VOLUMA
          </Link>
          <p>{copy.descriptor}</p>
        </div>
        <nav
          aria-label={locale === "fa" ? "پیوندهای پایین صفحه" : "Footer"}
          className="site-footer__nav"
        >
          {navItems.map((item) => (
            <Link href={item.href} key={item.href}>
              {item.label[locale]}
            </Link>
          ))}
          <Link href="/privacy">{copy.privacy}</Link>
        </nav>
      </div>
      <div className="site-footer__base">
        <span>{copy.location}</span>
        <span>{copy.copyright}</span>
      </div>
    </footer>
  );
}
