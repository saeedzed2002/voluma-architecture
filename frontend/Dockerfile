FROM node:24.20.0-bookworm-slim@sha256:ba849c60be29959425b8734d57b8b4b7d56f98edd9504c9af091d5281095a71e AS dependencies

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    NEXT_TELEMETRY_DISABLED=1

WORKDIR /app/frontend

COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN corepack enable && corepack pnpm install --frozen-lockfile

FROM dependencies AS builder

COPY frontend ./
RUN corepack pnpm build

FROM node:24.20.0-bookworm-slim@sha256:ba849c60be29959425b8734d57b8b4b7d56f98edd9504c9af091d5281095a71e AS runner

ENV NODE_ENV=production \
    NEXT_CACHE_DIR=/tmp/next-cache \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

WORKDIR /app

RUN groupadd --gid 10001 --system voluma \
    && useradd --uid 10001 --gid voluma --system --no-create-home voluma

COPY --chown=voluma:voluma --from=builder /app/frontend/.next/standalone ./
COPY --chown=voluma:voluma --from=builder /app/frontend/.next/static ./.next/static
COPY --chown=voluma:voluma --from=builder /app/frontend/public ./public

USER voluma

EXPOSE 3000

CMD ["node", "server.js"]
