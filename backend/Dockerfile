FROM python:3.14.7-slim-bookworm@sha256:416f0db2a2b561945630cef9877a7ea0581b27449eb9fd9df42f03e1b74b5b63 AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/voluma-venv

WORKDIR /app

RUN python -m pip install --no-cache-dir "uv==0.12.9"

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/alembic ./alembic
COPY backend/alembic.ini ./
COPY backend/app ./app

FROM python:3.14.7-slim-bookworm@sha256:416f0db2a2b561945630cef9877a7ea0581b27449eb9fd9df42f03e1b74b5b63 AS runner

ENV PATH="/opt/voluma-venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VOLUMA_MEDIA_ROOT=/var/lib/voluma-media

WORKDIR /app

RUN groupadd --gid 10001 --system voluma \
    && useradd --uid 10001 --gid voluma --system --no-create-home voluma \
    && install --directory --owner=voluma --group=voluma --mode=0750 /var/lib/voluma-media

COPY --chown=voluma:voluma --from=builder /opt/voluma-venv /opt/voluma-venv
COPY --chown=voluma:voluma --from=builder /app /app

USER voluma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
