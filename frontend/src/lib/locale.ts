import type { Locale } from "@/i18n/routing";

export function isLocale(value: string): value is Locale {
  return value === "en" || value === "fa";
}

export function directionForLocale(locale: Locale): "ltr" | "rtl" {
  return locale === "fa" ? "rtl" : "ltr";
}

export function alternateLocale(locale: Locale): Locale {
  return locale === "en" ? "fa" : "en";
}

export function formatYear(year: string, locale: Locale): string {
  return new Intl.NumberFormat(locale === "fa" ? "fa-IR" : "en-US", {
    useGrouping: false,
  }).format(Number(year));
}
