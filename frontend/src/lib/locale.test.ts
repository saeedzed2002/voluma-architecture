import { describe, expect, it } from "vitest";

import { alternateLocale, directionForLocale, formatYear, isLocale } from "./locale";

describe("locale helpers", () => {
  it("accepts only the public locale set", () => {
    expect(isLocale("en")).toBe(true);
    expect(isLocale("fa")).toBe(true);
    expect(isLocale("fr")).toBe(false);
  });

  it("maps locale direction and alternate locale", () => {
    expect(directionForLocale("en")).toBe("ltr");
    expect(directionForLocale("fa")).toBe("rtl");
    expect(alternateLocale("en")).toBe("fa");
    expect(alternateLocale("fa")).toBe("en");
  });

  it("uses locale-appropriate digits for project years", () => {
    expect(formatYear("2026", "en")).toBe("2026");
    expect(formatYear("2026", "fa")).toBe("۲۰۲۶");
  });
});
