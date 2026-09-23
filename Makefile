.PHONY: dev lint types test check format cov metrics demo demo-down

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

# Demonstração com dados fictícios em http://127.0.0.1:8081 (banco próprio em data/demo, recriado
# a cada início). Exige DEMO_SECRET_KEY no .env, diferente da SECRET_KEY do app real.
demo:
	@grep -q '^DEMO_SECRET_KEY=..*' .env || { echo "Defina DEMO_SECRET_KEY no .env (veja .env.example)"; exit 1; }
	@[ "$$(grep '^DEMO_SECRET_KEY=' .env | cut -d= -f2-)" != "$$(grep '^SECRET_KEY=' .env | cut -d= -f2-)" ] || { echo "DEMO_SECRET_KEY precisa ser diferente de SECRET_KEY"; exit 1; }
	docker compose --profile demo up -d --build demo
	@echo "Demo em http://127.0.0.1:8081 — login demo@example.com / demo-patrimonio"

demo-down:
	docker compose --profile demo stop demo
	docker compose --profile demo rm -f demo
