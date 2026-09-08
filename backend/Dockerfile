FROM python:3.14.7-slim-bookworm@sha256:9ab8d9c8514b44f90cf0029dd42fdd7e9e211e639c8b995304cc04568dee900f AS builder

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

FROM python:3.14.7-slim-bookworm@sha256:9ab8d9c8514b44f90cf0029dd42fdd7e9e211e639c8b995304cc04568dee900f AS runner

ENV PATH="/opt/voluma-venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VOLUMA_MEDIA_ROOT=/var/lib/voluma-media

WORKDIR /app

# Runtime dependencies are supplied exclusively by the frozen application virtual
# environment below. Removing distribution-maintenance installers keeps their vendored
# packages out of the production image and prevents runtime mutation.
RUN groupadd --gid 10001 --system voluma \
    && useradd --uid 10001 --gid voluma --system --no-create-home voluma \
    && install --directory --owner=voluma --group=voluma --mode=0750 /var/lib/voluma-media \
    && rm -rf /usr/local/lib/python3.14/ensurepip \
        /usr/local/lib/python3.14/site-packages/pip \
        /usr/local/lib/python3.14/site-packages/pip-*.dist-info \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.14

COPY --chown=voluma:voluma --from=builder /opt/voluma-venv /opt/voluma-venv
COPY --chown=voluma:voluma --from=builder /app /app

USER voluma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
