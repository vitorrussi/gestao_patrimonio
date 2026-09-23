# Gestão de Patrimônio

Webapp pessoal de gestão de patrimônio. Primeiro módulo: **imóveis** — quanto vale o
patrimônio (bruto, dívidas e líquido), quanto é preciso pagar por mês e o que vence e quando.

- Escopo funcional: [`ESCOPO_IMOVEIS.md`](ESCOPO_IMOVEIS.md)
- Stack, regras técnicas, testes e métricas: [`STACK_E_PLANO.md`](STACK_E_PLANO.md)
- Instruções para quem desenvolve (inclusive IA): [`CLAUDE.md`](CLAUDE.md)

## Stack em uma linha

Flask + SQLAlchemy 2.0 + Alembic + Pydantic + Flask-Login (Python 3.12, `uv`) com SQLite;
React + TypeScript + Vite + React Router + TanStack Query + Tailwind/shadcn/ui (Node 22, `npm`);
tudo empacotado em uma imagem Docker (Gunicorn serve a API em `/api` e o front buildado).

## Primeira vez

Pré-requisitos: [uv](https://docs.astral.sh/uv/), Node 22 + npm, Docker com Compose e `make`.

```bash
cp .env.example .env
# Gere a chave e cole em SECRET_KEY no .env:
python3 -c "import secrets; print(secrets.token_hex(32))"

cd frontend && npm install && cd ..   # dependências do front
cd backend && uv sync && cd ..        # dependências do back (o make também faz isso sozinho)
```

Variáveis do `.env` (detalhes em [`.env.example`](.env.example)):

| Variável | Obrigatória | Para quê |
|---|---|---|
| `SECRET_KEY` | sim | Assina o cookie de sessão. Sem ela o app não sobe. |
| `ALLOW_REGISTRATION` | não (padrão `true`) | Libera `/cadastro`. Crie sua conta e deixe `false` antes de publicar. |
| `DATABASE_URL` | não | Outro caminho para o SQLite. Por padrão, `data/app.db`. |

## Rodar em desenvolvimento

```bash
make dev
```

Aplica as migrações e sobe o Flask em http://127.0.0.1:8080 e o Vite em
**http://127.0.0.1:5173** (abra este; ele repassa `/api` para o Flask). `Ctrl+C` encerra os dois.

A porta 8080 é a mesma do Docker: rode `docker compose down` antes de `make dev`.

## Rodar com Docker

```bash
docker compose up --build        # http://127.0.0.1:8080
docker compose down              # para (os dados continuam em ./data)
```

- O container aplica as migrações (`alembic upgrade head`) e depois sobe o Gunicorn.
- O banco fica em `./data/app.db` no host (bind mount): recriar o container não apaga os dados.
- O container roda com um usuário comum com o mesmo UID/GID do host (padrão 1000). Se o seu
  for outro, exporte `UID` e `GID` antes do build.

## Testes e qualidade

| Comando | O que faz |
|---|---|
| `make check` | Tudo abaixo (lint, tipos e testes) nos dois lados. Tem que passar antes de todo commit. |
| `make lint` | Ruff (lint + formatação, complexidade ≤ 10) · ESLint (complexidade, tamanho, sonarjs) · Prettier |
| `make types` | pyright · `tsc -b` (TypeScript `strict`) |
| `make test` | pytest (unitários, Hypothesis, integração da API, migrações, constraints) · Vitest |
| `make format` | Corrige a formatação (Ruff e Prettier) |
| `make cov` | Cobertura dos cálculos (`app/services`); falha abaixo de 95% |
| `make metrics` | Cobertura geral, complexidade e manutenibilidade (radon) e duplicação (jscpd) |

Nova migração: `cd backend && uv run alembic revision --autogenerate -m "descrição"`. Revise o
arquivo gerado: o autogenerate não detecta renomeações (vira remover + criar) nem CHECKs novos.

## Métricas (seção 7 do `STACK_E_PLANO.md`)

`make metrics` mostra:

- **Cobertura** do backend inteiro e dos cálculos (meta: cálculos ~100%, resto 70–80%).
- **radon cc**: funções com complexidade ciclomática acima de 10 (deve sair vazio) e a média.
- **radon mi**: índice de manutenibilidade por arquivo (A = bom; acompanhar a tendência).
- **jscpd**: trechos duplicados em `backend/app` e `frontend/src` (sem testes, migrações e
  componentes gerados pelo shadcn). Não falha: serve para acompanhar e extrair repetições.

## Estrutura

```
backend/
  app/
    models/        tabelas (dinheiro em centavos no banco, Decimal no Python)
    services/      cálculos puros: dinheiro, patrimônio, vencimentos, autenticação
    repositories/  consultas, sempre filtradas pelo dono do imóvel
    schemas/       validação de entrada (Pydantic)
    routes/        endpoints /api
  migrations/      Alembic
  tests/           unit/, integration/
frontend/src/
  api/             cliente HTTP, tipos das respostas e hooks de dados (TanStack Query)
  features/        páginas: auth, dashboard, properties, commitments
  components/      layout, peças de formulário e exibição; ui/ = shadcn
  lib/             dinheiro, datas, percentuais, rótulos, erros da API
docker/entrypoint.sh · Dockerfile · docker-compose.yml · Makefile
```

## Checklist manual do fluxo completo

Para rodar depois de mudanças grandes ou antes de publicar, com `docker compose up --build`
a partir de um `data/` vazio. Use valores redondos para conferir as contas de cabeça.

1. **Acesso**
   - [ ] `/` sem login redireciona para `/login`.
   - [ ] Cadastro com e-mail inválido e senha curta mostra os erros em português.
   - [ ] Cadastro válido entra direto no painel ("Nenhum imóvel ativo cadastrado ainda").
2. **Imóvel**
   - [ ] Cadastrar "Apto Centro", apartamento, alugado, participação **50**, compra
     **350.000**, ITBI **7.000,00**, escritura **R$ 3.500,50**, UF `sc`, CEP `89201000`.
   - [ ] A ficha mostra UF "SC", CEP "89201-000" e aquisição total **R$ 360.500,50**.
3. **Valores**
   - [ ] Avaliação de **400.000**: valor atual R$ 400.000,00 e "Sua parte (50%)" R$ 200.000,00.
   - [ ] Financiamento com 1ª parcela no dia 15 e vencimento dia 10 → erro em português.
     Corrigir para o dia 10 → salva, com "Dívida estimada" = valor financiado.
   - [ ] Lançar saldo de **100.000**: patrimônio líquido **R$ 100.000,00** (caso do ESCOPO).
4. **Despesas e compromissos**
   - [ ] Despesa "IPTU — 10x", R$ 300,00, dia 10, início 01/02, 10 parcelas.
   - [ ] Compromissos: aparece de fevereiro a novembro, dezembro vem vazio; mês passado vencido
     = "Atrasado", vencimento de hoje = "A pagar".
   - [ ] Registrar pagamento com valor maior (juros): item "Pago", total pago com o valor real.
   - [ ] "Desfazer" volta o status; registrar de novo.
   - [ ] Editar a despesa: dia, periodicidade, início e parcelas aparecem travados.
5. **Painel e lista**
   - [ ] Painel: bruto, dívida e líquido batem com a ficha; contagem por tipo correta.
   - [ ] Editar o imóvel e desmarcar "Imóvel ativo": some do painel e dos compromissos;
     aparece em "Vendidos / inativos" na lista.
6. **Celular** (DevTools, 390 px de largura)
   - [ ] Menu vira ícone ☰ com gaveta lateral; lista vira cartões; formulários em uma coluna.
7. **Encerramento**
   - [ ] "Sair" volta ao login; abrir `/imoveis/1` redireciona para o login.
   - [ ] `docker compose up -d --force-recreate`: os dados continuam lá.
   - [ ] Excluir o imóvel pede confirmação e remove tudo ligado a ele.
