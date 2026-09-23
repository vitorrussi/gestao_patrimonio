# syntax=docker/dockerfile:1

# --- Estágio 1: build do frontend ---
FROM node:22-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Estágio 2: imagem final (Python + estáticos do front) ---
FROM python:3.12-slim AS final

ARG UID=1000
ARG GID=1000

ENV UV_PYTHON_PREFERENCE=only-system \
    PYTHONUNBUFFERED=1 \
    PATH="/app/backend/.venv/bin:$PATH"

RUN pip install --no-cache-dir uv==0.12.17 \
    && groupadd --gid "${GID}" app \
    && useradd --uid "${UID}" --gid "${GID}" --create-home --shell /usr/sbin/nologin app

WORKDIR /app/backend

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY backend/ ./
RUN uv sync --locked --no-dev

COPY --from=frontend-build /frontend/dist /app/frontend/dist
COPY docker/ /app/docker/
RUN chmod +x /app/docker/*.sh \
    && mkdir -p /app/data \
    && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
