.PHONY: dev lint types test check format

# Backend (Flask, porta 8080) e frontend (Vite, porta 5173) juntos; Ctrl+C encerra os dois.
# A porta 8080 é a mesma do Docker: rode `docker compose down` antes.
dev:
	@trap 'kill 0' INT TERM EXIT; \
	(cd backend && uv run alembic upgrade head && uv run flask --app app:create_app run --debug --port 8080) & \
	(cd frontend && npm run dev) & \
	wait

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && npm run lint

types:
	cd backend && uv run pyright
	cd frontend && npm run typecheck

test:
	cd backend && uv run pytest
	cd frontend && npm test

check: lint types test

format:
	cd backend && uv run ruff check --fix . && uv run ruff format .
	cd frontend && npm run format
