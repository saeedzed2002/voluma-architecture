import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
    server: {
      deps: {
        // next-intl imports the Next middleware entry point. Keep it in Vitest's
        // resolver so pnpm's isolated peer-dependency layout resolves next/server.
        inline: ["next-intl"],
      },
    },
    coverage: {
      include: ["src/lib/**/*.ts"],
    },
  },
});
