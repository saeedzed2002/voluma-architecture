import createNextIntlPlugin from "next-intl/plugin";
import type { NextConfig } from "next";

const withNextIntl = createNextIntlPlugin();

const nextConfig: NextConfig = {
  agentRules: false,
  allowedDevOrigins: ["127.0.0.1"],
  output: "standalone",
  poweredByHeader: false,
  reactStrictMode: true,
  async rewrites() {
    const apiBaseUrl = (
      process.env.VOLUMA_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"
    ).replace(/\/$/, "");
    return {
      afterFiles: [
        {
          // Managed derivatives always have media ID, derivative version, and file
          // segments. Keeping this rewrite narrow lets development fixture images in
          // public/media remain available through the Next.js static-file handler.
          destination: `${apiBaseUrl}/media/:mediaId/:derivativeVersion/:filename`,
          source: "/media/:mediaId/:derivativeVersion/:filename",
        },
      ],
    };
  },
};

export default withNextIntl(nextConfig);
