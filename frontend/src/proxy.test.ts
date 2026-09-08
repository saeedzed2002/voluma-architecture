import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";

import proxy from "./proxy";

describe("security proxy", () => {
  it("adds a per-request nonce CSP before localized rendering", () => {
    const response = proxy(new NextRequest("https://voluma.example/en"));
    const contentSecurityPolicy = response.headers.get("Content-Security-Policy");

    expect(contentSecurityPolicy).toContain("frame-ancestors 'none'");
    expect(contentSecurityPolicy).toMatch(/script-src 'self' 'nonce-[A-Za-z0-9+/=]+'/);
    expect(contentSecurityPolicy).toContain("style-src-attr 'unsafe-inline'");
    expect(response.headers.get("X-Content-Type-Options")).toBe("nosniff");
  });

  it("protects administrative pages without locale-routing them", () => {
    const response = proxy(new NextRequest("https://voluma.example/admin/login"));

    expect(response.headers.get("location")).toBeNull();
    expect(response.headers.get("Content-Security-Policy")).toContain("default-src 'self'");
    expect(response.headers.get("Referrer-Policy")).toBe("strict-origin-when-cross-origin");
  });
});
