#!/bin/sh
set -e

uv run alembic upgrade head

exec uv run gunicorn "app:create_app()" \
    --bind 0.0.0.0:8000 \
    --workers 2
