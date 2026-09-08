import { NextRequest, NextResponse } from "next/server";
import createMiddleware from "next-intl/middleware";

import { routing } from "./i18n/routing";

const internationalizationProxy = createMiddleware(routing);

function createContentSecurityPolicy(nonce: string, isDevelopment: boolean) {
  const scriptSource = ["'self'", `'nonce-${nonce}'`, "'strict-dynamic'"];
  if (isDevelopment) scriptSource.push("'unsafe-eval'");

  const directives = [
    "base-uri 'self'",
    "default-src 'self'",
    "font-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "img-src 'self' data: blob:",
    "object-src 'none'",
    "script-src " + scriptSource.join(" "),
    "style-src 'self'",
    "connect-src 'self'" + (isDevelopment ? " ws: wss:" : ""),
    "worker-src 'self' blob:",
  ];
  if (!isDevelopment) directives.push("upgrade-insecure-requests");
  return directives.join("; ");
}

function withSecurityHeaders(response: NextResponse, contentSecurityPolicy: string) {
  response.headers.set("Content-Security-Policy", contentSecurityPolicy);
  response.headers.set("Permissions-Policy", "camera=(), geolocation=(), microphone=()");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set("X-Content-Type-Options", "nosniff");
  return response;
}

export default function proxy(request: NextRequest) {
  const nonce = btoa(crypto.randomUUID());
  const contentSecurityPolicy = createContentSecurityPolicy(
    nonce,
    process.env.NODE_ENV !== "production",
  );
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("Content-Security-Policy", contentSecurityPolicy);
  requestHeaders.set("x-nonce", nonce);
  const securedRequest = new NextRequest(request, { headers: requestHeaders });

  const isAdministrativePath =
    request.nextUrl.pathname === "/admin" || request.nextUrl.pathname.startsWith("/admin/");
  if (isAdministrativePath) {
    return withSecurityHeaders(
      NextResponse.next({ request: { headers: requestHeaders } }),
      contentSecurityPolicy,
    );
  }

  return withSecurityHeaders(internationalizationProxy(securedRequest), contentSecurityPolicy);
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
