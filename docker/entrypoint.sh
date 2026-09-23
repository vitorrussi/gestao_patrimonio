#!/bin/sh
set -e

# Binários da .venv direto (PATH do Dockerfile): `uv run` sincronizaria o grupo dev no start.
alembic upgrade head

exec gunicorn "app:create_app()" \
    --bind 0.0.0.0:8000 \
    --workers 2
