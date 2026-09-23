.PHONY: dev lint types test check format cov metrics

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

# Cobertura dos services (cálculos): falha abaixo de 95%.
cov:
	cd backend && uv run pytest --cov=app/services --cov-report=term-missing --cov-fail-under=95

# Métricas da seção 7 do STACK_E_PLANO: cobertura, complexidade/manutenibilidade (radon) e duplicação (jscpd).
metrics: cov
	cd backend && uv run pytest -q --cov=app --cov-report=term:skip-covered | grep -E "TOTAL|passed"
	@echo "--- radon: funções com complexidade > 10 (nenhuma esperada) ---"
	cd backend && uv run radon cc app -n C -s
	@echo "--- radon: complexidade média ---"
	cd backend && uv run radon cc app -a -s | tail -1
	@echo "--- radon: índice de manutenibilidade (A = bom) ---"
	cd backend && uv run radon mi app -s
	@echo "--- jscpd: duplicação ---"
	frontend/node_modules/.bin/jscpd --config .jscpd.json
