#!/bin/sh
# Demonstração: a cada início, apaga o banco demo, recria pelas migrações e preenche
# com a carteira fictícia. O banco real nunca é tocado (o seed recusa caminho sem "demo").
set -e

case "$DATABASE_URL" in
    *demo*) ;;
    *) echo "DATABASE_URL do demo precisa apontar para um banco em data/demo" >&2; exit 1 ;;
esac
if [ -z "$SECRET_KEY" ]; then
    echo "DEMO_SECRET_KEY não definida no .env (veja .env.example)" >&2
    exit 1
fi

DB_FILE="${DATABASE_URL#sqlite:///}"
mkdir -p "$(dirname "$DB_FILE")"
rm -f "$DB_FILE" "$DB_FILE-wal" "$DB_FILE-shm"

alembic upgrade head
python -m scripts.seed_demo

exec gunicorn "app:create_app()" \
    --bind 0.0.0.0:8000 \
    --workers 2
