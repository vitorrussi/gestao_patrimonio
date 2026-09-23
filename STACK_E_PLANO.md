# Gestão de Patrimônio — Stack e Plano Técnico

Documento de referência técnica do projeto. Define a stack, os testes, as métricas de qualidade e a ordem de implementação da infraestrutura.

O escopo funcional (o que o app faz) será definido separadamente. Este documento trata só do **como**.

---

## 1. Stack

### Backend
| Item | Escolha |
|---|---|
| Linguagem | Python |
| Framework | Flask |
| ORM / migrações | SQLAlchemy + Alembic |
| Validação de entrada | Pydantic |
| Autenticação | Flask-Login, sessão em cookie, hash de senha (`werkzeug.security`) |
| Servidor de aplicação | Gunicorn (2–4 workers) |
| Configuração | `.env` + python-dotenv (fora do Git) |
| Dependências | uv |

### Banco de dados
| Item | Escolha |
|---|---|
| Banco | SQLite |
| Configuração | `PRAGMA journal_mode=WAL` e `PRAGMA busy_timeout=5000` |
| Migração futura (se necessário) | PostgreSQL, com `NUMERIC` para valores |

### Frontend
| Item | Escolha |
|---|---|
| Base | React + TypeScript (`strict`) + Vite |
| Rotas | React Router |
| Dados da API | TanStack Query |
| Visual | Tailwind CSS + shadcn/ui, responsivo |
| Formulários | React Hook Form + Zod |
| Gráficos | Recharts |
| Mobile | PWA (instalável pelo navegador, sem loja) |
| Dependências | npm |

### Infraestrutura
| Item | Escolha |
|---|---|
| Containers | Docker + docker compose |
| Imagem do app | Dockerfile multi-stage (Node → build do front; Python → imagem final) |
| Proxy / HTTPS | Caddy (container separado, imagem oficial) |
| Servidor | VPS com disco persistente (provedor a definir) |
| Backup | **Adiado.** Quando entrar: `sqlite3 ".backup"` via cron no host + envio para fora do servidor |
| Monitoramento de erros | Sentry |
| CI | GitHub Actions |

### Ferramentas de qualidade
| Área | Python | TypeScript |
|---|---|---|
| Lint / formatação | Ruff | ESLint (+ `eslint-plugin-sonarjs`) + Prettier |
| Tipos | pyright | `tsc --noEmit`, type-coverage |
| Complexidade | Ruff C901, radon | ESLint `complexity`, sonarjs |
| Código morto | vulture | knip |
| Segurança | bandit, pip-audit | npm audit |
| Duplicação | jscpd | jscpd |
| Testes | pytest, Hypothesis, mutmut | Vitest, Playwright |
| Carga | Locust | — |

---

## 2. Regras fixas do projeto

Valem desde o primeiro commit.

1. **Dinheiro nunca é `float`.** Use `Decimal` no Python e inteiros em centavos no banco.
2. **Toda query de dados do usuário filtra pelo usuário logado.**
3. **Todo bug vira um teste antes de ser corrigido.**
4. **Toda mudança em cálculo financeiro vem com teste novo ou atualizado.**
5. **Segredos só no `.env`**, nunca no código, na imagem ou no Git.
6. **Mudança no banco só via migração Alembic**, nunca alterando o schema na mão.
7. **Revisão de código gerado por IA:** procurar queries sem filtro de usuário, `float` em valores, `try/except` que engole erros e funções longas ou aninhadas demais.

---

## 3. Estrutura sugerida do repositório

```
/
├── backend/
│   ├── app/
│   │   ├── __init__.py        # create_app()
│   │   ├── config.py
│   │   ├── db.py              # engine, sessão, PRAGMAs do SQLite
│   │   ├── models/
│   │   ├── schemas/           # Pydantic
│   │   ├── routes/            # blueprints /api/...
│   │   └── services/          # lógica de negócio e cálculos
│   ├── migrations/            # Alembic
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── e2e/                   # Playwright
│   ├── package.json
│   └── vite.config.ts
├── docker/
│   ├── entrypoint.sh          # alembic upgrade head → gunicorn
│   └── Caddyfile
├── scripts/
│   └── backup.sh          # quando o backup for implementado
├── data/                      # SQLite (volume, fora do Git)
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
└── STACK_E_PLANO.md
```

A separação `routes/` → `services/` importa: os cálculos ficam em `services/` como funções puras, fáceis de testar sem banco e sem HTTP.

---

## 4. Plano por fases

Cada fase entrega algo funcionando e só adiciona o necessário. Não avance de fase com testes quebrando.

### Fase 0 — Fundação local com Docker

**Objetivo:** um "hello world" completo (front chamando a API, que lê o banco) rodando com um comando.

- [x] Repositório com a estrutura acima, `.gitignore` e `.env.example`
- [x] Backend: projeto com uv, `create_app()`, rota `GET /api/health`
- [x] Banco: SQLAlchemy com os PRAGMAs de WAL e busy_timeout aplicados em cada conexão
- [x] Alembic configurado, com uma migração inicial (mesmo que com uma tabela só)
- [x] Frontend: Vite + React + TypeScript (`strict`), uma página que chama `/api/health`
- [x] Proxy do Vite apontando `/api` para o Flask no desenvolvimento
- [x] `Dockerfile` multi-stage: build do front no estágio Node, `dist/` copiado para a imagem Python
- [x] Flask servindo os arquivos estáticos do `dist/` e a API em `/api`
- [x] `docker/entrypoint.sh`: `alembic upgrade head` e depois Gunicorn
- [x] `docker-compose.yml` só com o serviço `app`, porta local e bind mount `./data:/app/data`
- [x] `.dockerignore` excluindo `node_modules`, `.venv`, `.env`, `data/` e `.git`
- [x] Container rodando com usuário não-root
- [x] Ruff, ESLint, Prettier e `tsc --noEmit` configurados
- [x] pytest com um teste do `/api/health`

**Pronto quando:** `docker compose up --build` sobe o app, a página abre em `localhost`, e recriar o container não apaga o banco.

**Fluxo de desenvolvimento:** no dia a dia, rodar Flask (debug) e Vite dev server direto na máquina. O Docker serve para validar a imagem final.

---

### Fase 1 — Núcleo do backend com testes

**Objetivo:** base segura para construir as funcionalidades.

- [ ] Modelo de usuário, cadastro e login com Flask-Login
- [ ] Todas as rotas `/api` (exceto login e health) exigindo autenticação
- [ ] Tipo ou helper padrão para dinheiro (centavos no banco ↔ `Decimal` no Python)
- [ ] Validação de entrada com Pydantic em todas as rotas que recebem dados
- [ ] Primeiros modelos de domínio e migrações (conforme o escopo definido)
- [ ] Fixtures do pytest: app de teste, SQLite temporário por teste, usuário logado
- [ ] Testes unitários dos cálculos em `services/`
- [ ] Testes de integração dos endpoints (status 200/201/400/401/404)
- [ ] **Teste de isolamento:** usuário A não lê nem altera dados do usuário B
- [ ] Teste de migrações: upgrade do zero e downgrade da última
- [ ] Testes de propriedades com Hypothesis nos cálculos
- [x] Regra C901 do Ruff ativa (complexidade ≤ 10)

**Pronto quando:** a suíte roda em segundos, e a cobertura dos módulos de cálculo está perto de 100%.

---

### Fase 2 — CI e métricas automáticas

**Objetivo:** tudo que roda "a cada commit" passa a rodar sozinho.

- [ ] GitHub Actions: lint, formatação e tipos (backend e frontend)
- [ ] GitHub Actions: pytest com relatório de cobertura
- [ ] Limites de cobertura no CI (cálculos ~100%, resto 70–80%)
- [ ] bandit no CI
- [x] Regras do ESLint: `complexity`, `max-lines`, `max-lines-per-function`, sonarjs (complexidade cognitiva)
- [ ] jscpd no CI
- [ ] Build da imagem Docker no CI (garante que o Dockerfile não quebrou)
- [ ] pre-commit local com Ruff e Prettier (opcional, mas ajuda)

**Pronto quando:** um PR com lint, teste ou métrica quebrada fica vermelho no GitHub.

---

### Fase 3 — Frontend completo e E2E

**Objetivo:** interface usável no computador e no celular, testada de ponta a ponta.

- [ ] React Router, TanStack Query, Tailwind + shadcn/ui
- [ ] Formulários com React Hook Form + Zod
- [ ] Tela de login e fluxo de sessão (redirecionar quando não autenticado)
- [ ] Tipos TypeScript das respostas da API (à mão)
- [ ] Teste de contrato: respostas da API validadas contra os tipos/schemas do front
- [ ] Gráficos com Recharts
- [ ] Layout responsivo
- [ ] Vitest para lógica do front (formatação de moeda, datas etc.)
- [ ] Playwright: login → cadastrar → ver patrimônio → editar → excluir → logout
- [ ] Playwright rodando em viewport desktop e mobile
- [ ] type-coverage e knip configurados
- [ ] PWA: manifest, ícones, instalável no celular

**Pronto quando:** os fluxos principais passam no Playwright em desktop e mobile.

---

### Fase 4 — Produção

**Objetivo:** app no ar com HTTPS e deploy confiável.

- [ ] VPS criada, Docker instalado, acesso SSH só por chave
- [ ] Domínio apontando para a VPS
- [ ] Serviço `caddy` no `docker-compose.yml`, com HTTPS automático e proxy para o `app`
- [ ] Front e API no mesmo domínio (`/api/...`)
- [ ] Cookies de sessão com `Secure`, `HttpOnly` e `SameSite`
- [ ] `.env` de produção criado direto no servidor
- [ ] Smoke test pós-deploy (página abre, login funciona, API responde)
- [ ] Procedimento de deploy documentado (pull → build → up → smoke test)
- [ ] Procedimento de rollback documentado (voltar para a imagem anterior)
- [ ] pip-audit e npm audit antes do deploy

**Pronto quando:** o app está no ar com HTTPS e o deploy e o rollback seguem um procedimento documentado.

> **Backup:** adiado por decisão do projeto. Nesta fase o banco principal fica sem backup. Os itens de backup estão na Fase 6.

---

### Fase 5 — Observabilidade e robustez

**Objetivo:** saber quando algo quebra e conhecer os limites do sistema.

- [ ] Sentry no backend e no front
- [ ] Logs estruturados (com tempo de resposta por endpoint)
- [ ] Teste de concorrência: escritas simultâneas sem "database is locked" e sem perda de dados
- [ ] Teste de carga com Locust para saber quanto a VPS aguenta
- [ ] mutmut nos módulos de cálculo
- [ ] Lighthouse mobile (registrar a nota inicial)
- [ ] vulture no backend
- [ ] Rotina mensal (seção 6) iniciada

**Pronto quando:** erros em produção chegam até você, e você sabe quantos usuários simultâneos o sistema aguenta.

---

### Fase 6 — Evolução (só quando houver necessidade)

Nenhum destes itens tem data. Cada um entra quando aparecer o motivo.

| Item | Quando fazer |
|---|---|
| Migrar para PostgreSQL | Teste de carga ou uso real mostrando limite do SQLite, ou necessidade de mais de um servidor |
| Gerar tipos TS via OpenAPI | Quando manter os tipos à mão começar a gerar erros |
| Cotações automáticas (ex.: brapi.dev + tarefa agendada) | Planejado para o futuro. No início, os valores são lançados à mão |
| Separar containers | Quando algum componente precisar escalar ou ser atualizado de forma independente |
| `docker-compose.dev.yml` com hot reload | Se o desenvolvimento local fora do Docker começar a divergir da produção |
| **Backup do banco** | Quando for definido o destino externo. Itens: `scripts/backup.sh` (`.backup`, compactação, rotação de 7–30 cópias, envio para fora do servidor), cron diário no host, alerta em falha e primeiro teste de restauração |
| Backup em container dedicado | Depois do backup implementado, se o cron no host ficar difícil de manter |

---

## 5. Testes

### Por nível
| Nível | Ferramenta | O que cobre |
|---|---|---|
| Unitário | pytest | Cálculos financeiros, arredondamento, casos de borda |
| Propriedades | Hypothesis | Invariantes (ex.: soma das categorias = total) |
| Integração | pytest + SQLite temporário | Endpoints com banco real, validação, autenticação, isolamento entre usuários, rollback |
| Migrações | pytest + Alembic | Upgrade do zero e downgrade da última |
| Contrato | pytest / Vitest | Formato do JSON da API bate com o que o front espera |
| Front (lógica) | Vitest | Formatação de moeda, datas, helpers |
| E2E | Playwright | Fluxos principais, em desktop e mobile |
| Smoke | script simples | Após cada deploy: página, login, API |
| Concorrência | pytest ou script | Escritas simultâneas no SQLite |
| Carga | Locust | Limite de usuários simultâneos na VPS |
| Mutação | mutmut | Se os testes dos cálculos realmente detectam erros |

### Casos de borda obrigatórios nos cálculos
- Carteira vazia
- Ativo com posição zerada
- Venda maior que a posição
- Datas iguais e anos bissextos
- Valores negativos
- Arredondamento: 0,01, 0,10, 33,33 × 3 (nenhum centavo pode sumir ou aparecer)
- Aportes e retiradas no meio do período de rentabilidade

---

## 6. Rotina de qualidade

### A cada commit/push (CI)
- Lint, formatação e tipos
- Testes unitários, de propriedades, de integração, de migrações e de contrato
- Cobertura dentro dos limites
- bandit
- Complexidade, tamanho e duplicação dentro dos limites
- Build da imagem Docker

### Semanal ou antes de cada deploy
- E2E (desktop + mobile)
- Build de produção do front sem erros ou warnings novos
- pip-audit e npm audit
- Teste de concorrência

### Após cada deploy
- Smoke test

### Mensal
- Restaurar um backup e conferir os dados (quando o backup existir)
- Comparar o saldo do app com o extrato real (banco/corretora)
- mutmut nos módulos de cálculo
- Revisar dependências desatualizadas
- Lighthouse mobile
- vulture e knip (código morto)

### Ocasional
- Teste de carga (e sempre que o uso crescer)

---

## 7. Métricas e limites

### Código
| Métrica | Ferramenta | Limite / referência |
|---|---|---|
| Complexidade ciclomática | Ruff C901 / radon, ESLint `complexity` | ≤ 10 por função |
| Complexidade cognitiva | eslint-plugin-sonarjs | ≤ 15 por função |
| Tamanho de função | ESLint `max-lines-per-function` | ~50 linhas |
| Tamanho de arquivo | ESLint `max-lines` | ~300–400 linhas |
| Índice de manutenibilidade | radon mi | Acompanhar tendência |
| Duplicação | jscpd | Acompanhar; extrair repetições |
| Código morto | vulture, knip | Zero, ou justificado |
| Cobertura de tipos (TS) | type-coverage | Perto de 100%, poucos `any` |

### Testes
| Métrica | Limite / referência |
|---|---|
| Testes passando | 100%, nenhum ignorado sem motivo |
| Cobertura dos módulos de cálculo | Perto de 100% |
| Cobertura do restante | 70–80% |
| Mutation score (cálculos) | Quanto mais alto, melhor; investigar mutantes sobreviventes |
| Tempo da suíte unitária | Segundos |

### Frontend
| Métrica | Referência |
|---|---|
| Tamanho do bundle (`vite build`) | Investigar saltos grandes |
| Lighthouse mobile | Não deixar cair |

### Produção
| Métrica | Referência |
|---|---|
| Taxa de erros 5xx / exceções | Investigar qualquer aumento |
| Tempo de resposta dos endpoints principais | Investigar acima de algumas centenas de ms |
| Tamanho do banco | Acompanhar crescimento |
| Backup diário (quando existir) | Sucesso todo dia, com alerta em falha |
| Certificado HTTPS | Válido (o Caddy renova sozinho) |

---

## 8. Decisões em aberto

### Decidido
- [x] Verificador de tipos Python: **pyright**
- [x] Gerenciador de pacotes do front: **npm**
- [x] Valores: **lançados à mão no início**; cotações automáticas no futuro (Fase 6)
- [x] Backup: **adiado**; por enquanto o banco principal fica sem backup

### Em aberto
- [ ] Escopo funcional do app (o que ele faz). Será definido depois
- [ ] Provedor da VPS. Ignorado por enquanto
- [ ] Destino do backup externo (Google Drive, Backblaze, S3...). Ignorado por enquanto
