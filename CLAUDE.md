# Gestão de Patrimônio

Webapp pessoal de gestão de patrimônio. Primeiro módulo: imóveis.

## Documentos de referência (fonte da verdade)

- `STACK_E_PLANO.md`: stack, regras técnicas, testes, métricas e fases de infraestrutura.
- `ESCOPO_IMOVEIS.md`: escopo funcional do módulo de imóveis (entidades, campos, regras de negócio, casos de teste).

Leia os dois antes de planejar qualquer trabalho. Se uma instrução contradisser esses documentos, pare e pergunte.

## Regras obrigatórias

1. Dinheiro: inteiro em centavos no banco e `Decimal` no Python. Nunca `float` em nenhuma camada. No front, trafegar valores em centavos (inteiros) e formatar como BRL só na exibição.
2. Toda query de dados do usuário filtra pelo usuário logado.
3. Mudanças no banco só via migrações Alembic.
4. Segredos só no `.env` (manter `.env.example` atualizado). Nada sensível no código, na imagem ou no Git.
5. Lógica de negócio e cálculos em `backend/app/services/` como funções puras, separadas das rotas.
6. Vencimentos são calculados na hora, não gravados no banco. Pagamento referencia (origem + data de vencimento de referência), com par único.
7. Complexidade ciclomática ≤ 10 por função. Funções curtas, sem aninhamento profundo.
8. Sem `try/except` genérico que engula erros.
9. Não adicionar dependências fora da stack definida sem perguntar antes.
10. Nomes no código (variáveis, funções, classes, tabelas) em inglês. Textos da interface em português do Brasil. Valores de enum conforme o `ESCOPO_IMOVEIS.md`.
11. Todo bug corrigido ganha um teste que o reproduz. Toda mudança em cálculo vem com teste novo ou atualizado.
12. Não implementar itens fora da fase atual, nem "já deixando pronto".
13. Estilos só com os tokens de tema do shadcn/ui (variáveis CSS) e classes utilitárias do Tailwind. Não usar cores, fontes ou tamanhos fixos nos componentes.

## Stack

- Backend: Python, Flask, SQLAlchemy 2.0 (`Mapped[...]`), Alembic, Pydantic, Flask-Login, Gunicorn, uv.
- Banco: SQLite com `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000` e `PRAGMA foreign_keys=ON` em cada conexão (as chaves estrangeiras ficam desligadas só durante as migrações).
- Frontend: React + TypeScript (`strict`) + Vite, React Router, TanStack Query, Tailwind CSS + shadcn/ui, React Hook Form + Zod, npm.
- Qualidade: Ruff (inclui C901), pyright, ESLint (`complexity`, `max-lines`, `max-lines-per-function`, `eslint-plugin-sonarjs`), Prettier, `tsc --noEmit`, pytest, Hypothesis, Vitest.
- Docker: Dockerfile multi-stage (Node faz o build do front; a imagem Python serve `/api` e os estáticos do `dist/`), entrypoint com `alembic upgrade head` e depois Gunicorn, compose com o serviço `app` e bind mount `./data:/app/data`, usuário não-root.

Estrutura de pastas: seção 3 do `STACK_E_PLANO.md`.

## Comandos

Rodar da raiz do repositório. Pré-requisitos: `uv`, Node 22 e `npm install` em `frontend/`.

- Primeira vez: `cp .env.example .env` e preencher `SECRET_KEY` (o comando para gerar está no arquivo). Sem ela, `make dev` e o Docker não sobem. Os testes não precisam do `.env`.

- Dev: `make dev`. Aplica as migrações e sobe o Flask em http://127.0.0.1:8090 e o Vite em http://127.0.0.1:5173 (proxy `/api`). Usa banco próprio (`data/dev/app.db`) e não conflita com o Docker (8080 e 8081).
- Lint + formatação: `make lint` (Ruff + ESLint + Prettier). Para corrigir a formatação: `make format`.
- Tipos: `make types` (pyright + `tsc -b`)
- Testes: `make test` (pytest + Vitest)
- Tudo (`check`): `make check`
- Cobertura dos services: `make cov` (falha abaixo de 95%)
- Métricas (cobertura geral, radon, jscpd): `make metrics`
- Demonstração com dados fictícios: `make demo` → http://127.0.0.1:8081 (`demo@example.com` / `demo-patrimonio`); `make demo-down` para parar. Ao mudar modelos, mantenha `backend/scripts/seed_demo.py` em dia (o teste `test_seed_demo.py` quebra se não estiver).
- Nova migração: `cd backend && uv run alembic revision --autogenerate -m "descrição"`. Revise o arquivo gerado: o autogenerate não detecta renomeações (vira remover + criar) nem mudanças em CHECK.
- Docker: `docker compose up -d --build` → http://127.0.0.1:8080 (reinicia sozinho com o Docker, `restart: unless-stopped`)

## Forma de trabalho

- Trabalhar em etapas. Ao final de cada uma, parar e esperar aprovação.
- Em cada parada, entregar: resumo e arquivos alterados, comandos para verificar, resultado de lint/tipos/testes (tudo passando), pontos que merecem revisão atenta e decisões tomadas que não estavam nos documentos.
- O dono do projeto não domina React: nas etapas de frontend, explicar brevemente cada componente, hook e fluxo de dados novo.
- Commits pequenos e com mensagens claras.
- Ao concluir uma etapa, marcar os checkboxes correspondentes nos documentos de referência.
- Em caso de ambiguidade, perguntar em vez de supor.
