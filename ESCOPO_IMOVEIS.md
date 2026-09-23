# Gestão de Patrimônio — Escopo Funcional: Imóveis

Documento de referência funcional do módulo de imóveis. Define **o que** o app faz. A parte técnica (stack, testes, fases de infraestrutura) está em `STACK_E_PLANO.md`.

---

## 1. Objetivo

Organizar vários imóveis, de vários tipos, financiados ou não, para responder três perguntas:

1. **Quanto vale o meu patrimônio?** (bruto, dívidas e líquido)
2. **Quanto preciso pagar por mês?**
3. **O que vence e quando?**

Princípio de organização: separar **o imóvel** (o que ele é) das **coisas que acontecem com ele ao longo do tempo** (valores, financiamento, despesas, pagamentos, contratos).

---

## 2. Regras de negócio

1. **Dinheiro em centavos (inteiro) no banco e `Decimal` no Python.** Nunca `float`.
2. **Patrimônio líquido do imóvel = valor de mercado mais recente × % de participação − saldo devedor dos financiamentos.**
3. **Valor de mercado é histórico:** cada avaliação é um registro novo (data + valor + fonte). O valor "atual" é a avaliação mais recente.
4. **Saldo devedor é lançado à mão** a partir do extrato do banco. Simular a tabela SAC/Price fica para depois, como estimativa.
5. **Despesas recorrentes geram vencimentos; pagamentos quitam vencimentos.** O status de um vencimento é: `a pagar`, `pago` ou `atrasado` (a pagar e com data passada).
6. **Valor de aquisição não muda com o mercado.** Ele só aumenta com benfeitorias registradas (é o valor usado no IR).
7. **Todos os dados pertencem a um usuário.** Toda consulta filtra pelo usuário logado.

---

## 3. Entidades e campos

Campos marcados com **(MVP)** entram na primeira versão. Os demais podem ser adicionados depois.

### 3.1 Imóvel

**Identificação**
| Campo | Tipo | Observação |
|---|---|---|
| apelido **(MVP)** | texto | Ex.: "Apto Centro", "Terreno Pirabeiraba" |
| tipo **(MVP)** | enum | casa, casa_condominio, apartamento, terreno, terreno_condominio, sala_comercial, loja, galpao, predio, chacara_sitio, fazenda, vaga_garagem, box, outro. Lista ampla de propósito: os tipos reais ainda não estão todos mapeados |
| uso **(MVP)** | enum | moradia_propria, alugado, vazio, comercial_proprio, em_construcao |
| logradouro, número, complemento, bairro, cidade, UF, CEP **(MVP)** | texto | |
| área do terreno (m²) | decimal | |
| área construída (m²) | decimal | |
| quartos, vagas, andar | inteiro | Opcionais |
| observações | texto longo | |

**Documentação**
| Campo | Tipo | Observação |
|---|---|---|
| matrícula **(MVP)** | texto | Número da matrícula no cartório |
| cartório de registro **(MVP)** | texto | |
| inscrição imobiliária **(MVP)** | texto | Número do IPTU na prefeitura |
| condomínio (nome) | texto | Apartamentos e condomínios fechados |
| contato do síndico/administradora | texto | |
| CCIR / NIRF | texto | Só imóveis rurais (ITR) |

**Propriedade**
| Campo | Tipo | Observação |
|---|---|---|
| % de participação **(MVP)** | decimal (0–100) | Padrão 100 |
| coproprietários | texto | Nomes, se houver. Texto livre por enquanto; pode virar cadastro próprio de pessoas no futuro |
| data de aquisição **(MVP)** | data | |
| forma de aquisição **(MVP)** | enum | compra, heranca, doacao, construcao, outro |
| ativo **(MVP)** | booleano | Falso quando vendido; o imóvel sai dos totais, mas o histórico fica |

### 3.2 Valores

**Aquisição** (um por imóvel)
| Campo | Tipo | Observação |
|---|---|---|
| valor de compra **(MVP)** | dinheiro | |
| ITBI **(MVP)** | dinheiro | |
| escritura e registro **(MVP)** | dinheiro | |
| valor total de aquisição **(MVP)** | calculado | Soma dos anteriores + benfeitorias |

**Avaliação de mercado** (várias por imóvel)
| Campo | Tipo | Observação |
|---|---|---|
| data **(MVP)** | data | |
| valor **(MVP)** | dinheiro | |
| fonte **(MVP)** | enum | estimativa_propria, corretor, laudo, anuncio_similar, outro |
| observação | texto | |

**Valor venal** (um por ano)
| Campo | Tipo | Observação |
|---|---|---|
| ano | inteiro | |
| valor venal | dinheiro | Vem no carnê do IPTU |

**Benfeitoria** (várias por imóvel)
| Campo | Tipo | Observação |
|---|---|---|
| data | data | |
| descrição | texto | Ex.: "Ampliação da cozinha" |
| valor | dinheiro | Soma no valor de aquisição (IR) |
| tem nota fiscal | booleano | Só benfeitorias comprovadas contam no IR |

### 3.3 Financiamento

Zero, um ou vários por imóvel (ex.: banco + parcelamento com construtora).

| Campo | Tipo | Observação |
|---|---|---|
| credor **(MVP)** | texto | Banco, construtora etc. |
| número do contrato **(MVP)** | texto | |
| valor financiado **(MVP)** | dinheiro | |
| entrada | dinheiro | |
| FGTS utilizado | dinheiro | |
| sistema de amortização **(MVP)** | enum | sac, price, outro |
| taxa de juros anual **(MVP)** | decimal (%) | |
| indexador **(MVP)** | enum | tr, ipca, prefixado, outro |
| prazo total (meses) **(MVP)** | inteiro | |
| data da primeira parcela **(MVP)** | data | |
| dia de vencimento **(MVP)** | inteiro (1–31) | |
| valor da parcela atual **(MVP)** | dinheiro | Lançado à mão; alimenta os compromissos do mês |
| seguros MIP/DFI e taxa de administração | dinheiro | Componentes da parcela |
| quitado | booleano | |

**Registro de saldo devedor** (vários por financiamento)
| Campo | Tipo | Observação |
|---|---|---|
| data **(MVP)** | data | Data do extrato |
| saldo devedor **(MVP)** | dinheiro | O mais recente é o saldo atual |

**Amortização extra** (várias por financiamento)
| Campo | Tipo | Observação |
|---|---|---|
| data | data | |
| valor | dinheiro | |
| efeito | enum | reduzir_prazo, reduzir_parcela |

### 3.4 Despesa recorrente

Estrutura genérica para tudo que se paga periodicamente.

| Campo | Tipo | Observação |
|---|---|---|
| tipo **(MVP)** | enum | iptu, condominio, cota_extra, seguro, agua, luz, gas, internet, taxa_lixo, itr, laudemio_foro, manutencao, outro |
| descrição **(MVP)** | texto | Ex.: "IPTU 2026 — parcelado em 10x" |
| valor **(MVP)** | dinheiro | Valor de cada vencimento |
| periodicidade **(MVP)** | enum | mensal, bimestral, trimestral, semestral, anual, unica |
| dia de vencimento **(MVP)** | inteiro (1–31) | |
| data de início **(MVP)** | data | |
| data de fim / nº de parcelas **(MVP)** | data / inteiro | Ex.: IPTU parcelado em 10x |
| responsável pelo pagamento | enum | proprietario, inquilino (importante com aluguel) |
| ativa **(MVP)** | booleano | |

**Particularidades do IPTU:** registrar se foi pago à vista (com desconto) ou parcelado, e o valor venal do ano (seção 3.2).

A **parcela do financiamento** também aparece nos compromissos do mês, mas vem da seção 3.3, não daqui.

### 3.5 Vencimento e pagamento

**Vencimento** (calculado na hora, **não é gravado no banco**)

Os vencimentos são gerados em tempo de consulta a partir das regras das despesas recorrentes e dos financiamentos (periodicidade, dia de vencimento, início, fim/nº de parcelas). Cada vencimento calculado tem:

| Campo | Tipo | Observação |
|---|---|---|
| origem **(MVP)** | referência | Despesa recorrente ou financiamento |
| data de vencimento **(MVP)** | data | Calculada pela regra de recorrência |
| valor previsto **(MVP)** | dinheiro | Valor da despesa ou parcela |
| status **(MVP)** | calculado | pago (existe pagamento para origem + data), atrasado (sem pagamento e data passada), a_pagar |

A lógica de cálculo fica numa função pura em `services/` (entrada: regras + período; saída: lista de vencimentos), fácil de testar sem banco.

**Pagamento**
| Campo | Tipo | Observação |
|---|---|---|
| origem **(MVP)** | referência | Despesa recorrente ou financiamento |
| data de vencimento de referência **(MVP)** | data | Identifica qual vencimento calculado foi quitado. Par (origem, data) único |
| data do pagamento **(MVP)** | data | |
| valor pago **(MVP)** | dinheiro | Pode incluir juros/multa |
| forma | enum | pix, boleto, debito_automatico, cartao, outro |
| comprovante | arquivo | Ver seção 3.7 |
| observação | texto | |

> **Decidido:** vencimentos calculados na hora. Pode ser revisto após testes. Se for preciso editar um vencimento específico (ex.: valor diferente só naquele mês), a alternativa é passar a gravá-los antecipadamente.
>
> **Atenção:** como o pagamento aponta para (origem + data), alterar o dia de vencimento ou a periodicidade de uma despesa já paga pode deixar pagamentos antigos sem vencimento correspondente. No MVP, a regra é: mudanças na despesa valem só para vencimentos futuros; para mudar a regra, encerrar a despesa (data de fim) e criar uma nova.

### 3.6 Locação (pós-MVP — decidido: fica fora do MVP)

**Contrato de locação**
| Campo | Tipo | Observação |
|---|---|---|
| inquilino (nome, contato) | texto | |
| valor do aluguel | dinheiro | |
| dia de vencimento | inteiro | |
| início, fim, prazo | datas / inteiro | |
| índice de reajuste | enum | igpm, ipca, outro |
| mês de reajuste | inteiro | |
| garantia | enum | caucao, fiador, seguro_fianca, titulo_capitalizacao, nenhuma |
| imobiliária e taxa de administração | texto / % | |
| despesas pagas pelo inquilino | lista | Ex.: IPTU, condomínio ordinário |

**Recebimento de aluguel:** mesma estrutura de vencimento/pagamento, mas como receita.

### 3.7 Documentos (pós-MVP)

Arquivos ligados a um imóvel (ou a um financiamento, contrato ou pagamento).

| Campo | Tipo | Observação |
|---|---|---|
| categoria | enum | escritura, matricula, contrato_compra, contrato_financiamento, contrato_locacao, carne_iptu, apolice_seguro, nota_benfeitoria, comprovante, outro |
| nome do arquivo | texto | |
| data do documento | data | |
| caminho do arquivo | texto | |

> **Técnico:** arquivos ficam em pasta no volume do Docker (ex.: `data/uploads/`), nunca dentro do SQLite. O banco guarda só o caminho. Validar tipo e tamanho no upload. Quando os documentos entrarem, o backup deixa de ser opcional.

---

## 4. Telas e visões

### MVP
- **Lista de imóveis:** apelido, tipo, uso, valor de mercado atual, saldo devedor e patrimônio líquido.
- **Cadastro / edição de imóvel.**
- **Ficha do imóvel:** dados, valores, financiamentos, despesas recorrentes e pagamentos num lugar só.
- **Painel geral:**
  - patrimônio bruto (soma dos valores de mercado × participação);
  - dívida total (soma dos saldos devedores);
  - patrimônio líquido;
  - quantidade de imóveis por tipo.
- **Compromissos do mês:** tudo que vence no mês, com status (pago, a pagar, atrasado) e total.
- **Registrar pagamento** a partir de um vencimento.

### Pós-MVP
- **Próximos vencimentos:** 30, 60 e 90 dias, ou em formato de calendário.
- **Custo anual por imóvel:** IPTU + condomínio + seguro + parcelas + manutenção.
- **Resultado mensal por imóvel:** receita de aluguel − despesas.
- **Evolução do patrimônio:** gráfico a partir do histórico de avaliações e de saldo devedor.
- **Visão para o Imposto de Renda:** valor de aquisição + benfeitorias, aluguéis recebidos por mês (carnê-leão), saldo de financiamento em 31/12, pagamentos do ano.

---

## 5. Roadmap funcional

### Versão 1 — MVP
- [x] Cadastro de imóvel (identificação, tipo, uso, endereço, matrícula, inscrição do IPTU, participação, aquisição)
- [x] Valor de aquisição (compra + ITBI + escritura/registro)
- [x] Histórico de avaliações de mercado
- [x] Financiamento com parcela e saldo devedor lançados à mão
- [x] Despesas recorrentes genéricas (IPTU, condomínio, seguro etc.)
- [x] Vencimentos e registro de pagamentos
- [x] Painel geral e compromissos do mês
- [x] Marcar imóvel como vendido/inativo

### Versão 2
- [ ] Próximos vencimentos / calendário
- [ ] Locação: contratos e recebimentos
- [ ] Documentos e comprovantes (upload) — **exige backup implementado**
- [ ] Benfeitorias
- [ ] Valor venal por ano
- [ ] Custo anual e resultado mensal por imóvel

### Versão 3
- [ ] Gráfico de evolução do patrimônio
- [ ] Visão para o Imposto de Renda
- [ ] Amortizações extras
- [ ] Simulação da tabela SAC/Price (estimativa)
- [ ] Lembretes de vencimento (e-mail ou notificação do PWA)

### Futuro
- [ ] Reajuste automático de aluguel por índice (IGP-M/IPCA)
- [ ] Cotações e índices automáticos
- [ ] Outros tipos de bens (veículos, investimentos, contas) reaproveitando a estrutura bem → valores → despesas → pagamentos

---

## 6. Casos de teste importantes

Complementam os testes definidos em `STACK_E_PLANO.md`.

- Patrimônio líquido com participação parcial (ex.: 50% de um imóvel de R$ 400.000,00 com saldo devedor de R$ 100.000,00).
- Imóvel sem avaliação de mercado (não pode quebrar o painel; deve aparecer como "sem valor").
- Imóvel sem financiamento e imóvel com dois financiamentos.
- Financiamento quitado não entra na dívida nem nos compromissos do mês.
- Imóvel inativo/vendido não entra nos totais.
- Valor de mercado atual = avaliação com a data mais recente, não a última cadastrada.
- Despesa com dia de vencimento 31 em meses com 30 dias e em fevereiro.
- IPTU parcelado em 10x gera exatamente 10 vencimentos.
- Despesa anual, semestral e única gerando as datas corretas.
- Vencimento vira "atrasado" no dia seguinte à data, não no próprio dia.
- Pagamento com valor diferente do previsto (juros/multa) quita o vencimento.
- Totais do mês não perdem nem ganham centavos.
- Usuário não acessa imóveis, despesas ou pagamentos de outro usuário.
- Vencimento calculado aparece como "pago" quando existe pagamento com a mesma origem e data de referência.
- Não é possível registrar dois pagamentos para o mesmo par (origem, data de referência).
- Despesa encerrada (data de fim) não gera vencimentos depois do fim, mas mantém os pagamentos antigos.
- Cálculo de vencimentos para um período (ex.: um mês) retorna só os vencimentos daquele período.

---

## 7. Decisões

### Decidido
- [x] **Locação:** fora do MVP; entra na Versão 2
- [x] **Vencimentos:** calculados na hora, sem gravar no banco (pode ser revisto após testes; ver seção 3.5)
- [x] **Tipos de imóvel e despesa:** lista ampla mantida. Tipos confirmados até agora: terrenos, casas (dentro e fora de condomínio) e apartamentos; outros tipos ainda não mapeados
- [x] **Coproprietários:** texto livre por enquanto; talvez vire cadastro próprio de pessoas depois

### Em aberto
- [ ] Revisar as listas de tipos de imóvel e despesa depois de cadastrar os imóveis reais
