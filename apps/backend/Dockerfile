FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

ARG UV_VERSION=0.8.15
ARG UV_SYNC_ARGS=--no-dev

RUN pip install --no-cache-dir "uv==${UV_VERSION}" \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/storage \
    && chown appuser:appuser /app/storage

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen ${UV_SYNC_ARGS} \
    && rm -rf "${UV_CACHE_DIR}"

COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser migrations ./migrations
COPY --chown=appuser:appuser scripts ./scripts
COPY --chown=appuser:appuser seeds ./seeds
COPY --chown=appuser:appuser alembic.ini ./alembic.ini

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
