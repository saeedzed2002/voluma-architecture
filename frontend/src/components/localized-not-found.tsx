"use client";

import { useLocale } from "next-intl";

import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";

export function LocalizedNotFound() {
  const locale = useLocale() as Locale;
  const isPersian = locale === "fa";

  return (
    <main className="not-found section-shell">
      <p>404</p>
      <h1>{isPersian ? "این صفحه پیدا نشد." : "This page was not found."}</h1>
      <p>
        {isPersian
          ? "ممکن است نشانی تغییر کرده باشد یا این محتوا هنوز منتشر نشده باشد."
          : "The address may have changed or this content may not be published yet."}
      </p>
      <Link className="text-link" href="/">
        {isPersian ? "بازگشت به خانه" : "Return home"}
      </Link>
    </main>
  );
}
