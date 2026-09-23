import type { FieldHelp, HelpSection } from '../types'

/** Chave = `name` do campo no formulário de financiamento (`FinancingFormValues`). */
export const financingHelp = {
  mode: {
    id: 'financing-mode',
    label: 'Situação do financiamento',
    description:
      'Só existe na hora de cadastrar; não é gravada em lugar nenhum. Decide se a tela pede a data/prazo do contrato inteiro ou só o que falta pagar.',
    options: [
      {
        value: 'novo',
        label: 'Novo financiamento',
        effect: 'Pede a data da 1ª parcela e o prazo total do contrato, como sempre foi.',
      },
      {
        value: 'existente',
        label: 'Financiamento já em andamento',
        effect:
          'Pede a data da próxima parcela e o prazo restante (em vez da 1ª parcela e do prazo total) e exige lançar o saldo devedor atual. Funciona porque os vencimentos só são calculados dali para a frente — não é preciso saber quando o contrato começou de fato nem quantas parcelas já foram pagas fora do sistema.',
      },
    ],
  },
  lender: {
    id: 'financing-lender',
    label: 'Credor',
    description: 'Quem financiou: o banco ou a construtora.',
    format: 'Texto livre, até 100 caracteres.',
    examples: ['Caixa Econômica Federal', 'Construtora XPTO'],
    constraints: ['Obrigatório.'],
  },
  contract_number: {
    id: 'financing-contract_number',
    label: 'Número do contrato',
    description: 'Só para referência sua (não aparece em nenhum cálculo).',
    format: 'Texto livre, até 50 caracteres.',
    examples: ['123456789-0'],
    constraints: ['Opcional.'],
  },
  financed_amount: {
    id: 'financing-financed_amount',
    label: 'Valor financiado (R$)',
    description:
      'O valor total do empréstimo na assinatura do contrato. Não muda depois — é um valor histórico, diferente do saldo devedor (lançado à parte, que cai conforme você paga).',
    format: 'Reais com vírgula decimal.',
    examples: ['300.000,00', '85000,50'],
    constraints: [
      'Obrigatório.',
      'Se não houver nenhum saldo devedor lançado ainda, a dívida do imóvel é estimada como este valor.',
    ],
  },
  current_installment: {
    id: 'financing-current_installment',
    label: 'Parcela atual (R$)',
    description:
      'O valor da parcela de agora, lançado à mão sempre que mudar (ex.: reajuste anual). É esse valor que aparece nos compromissos de cada mês — o app não recalcula a parcela sozinho.',
    format: 'Reais com vírgula decimal.',
    examples: ['1.500,00'],
    constraints: ['Obrigatório.'],
  },
  amortization_system: {
    id: 'financing-amortization_system',
    label: 'Sistema de amortização',
    description:
      'Só informativo hoje — nenhum cálculo do app muda de acordo com essa escolha. A parcela usada nos compromissos é sempre a de "Parcela atual", lançada à mão. Simular a evolução da tabela SAC/Price está planejada para uma fase futura.',
    options: [
      {
        value: 'sac',
        label: 'SAC',
        effect:
          'Não afeta nenhum cálculo hoje. Na prática, é o sistema em que a parcela cai mês a mês.',
      },
      {
        value: 'price',
        label: 'Price',
        effect: 'Não afeta nenhum cálculo hoje. Na prática, é o sistema de parcela fixa.',
      },
      { value: 'outro', label: 'Outro', effect: 'Não afeta nenhum cálculo hoje.' },
    ],
  },
  interest_index: {
    id: 'financing-interest_index',
    label: 'Indexador',
    description:
      'Só informativo hoje — nenhum cálculo do app aplica correção automática pelo índice. Serve para você lembrar a que seu contrato está atrelado.',
    options: [
      { value: 'tr', label: 'TR', effect: 'Não afeta nenhum cálculo hoje.' },
      { value: 'ipca', label: 'IPCA', effect: 'Não afeta nenhum cálculo hoje.' },
      { value: 'prefixado', label: 'Prefixado', effect: 'Não afeta nenhum cálculo hoje.' },
      { value: 'outro', label: 'Outro', effect: 'Não afeta nenhum cálculo hoje.' },
    ],
  },
  annual_interest_rate: {
    id: 'financing-annual_interest_rate',
    label: 'Juros ao ano (%)',
    description: 'Só informativo hoje — não entra em nenhum cálculo do app.',
    format: 'Número com vírgula decimal, até 4 casas.',
    examples: ['9,5', '11,25'],
    constraints: ['Obrigatório.', 'De 0 a 1000.'],
  },
  term_months: {
    id: 'financing-term_months',
    label: 'Prazo (meses)',
    description:
      'Quantos meses de parcela o app deve gerar, contando a partir do mês da data ao lado ("Data da 1ª parcela" ou "Data da próxima parcela", dependendo da situação escolhida).',
    format: 'Número inteiro de meses.',
    examples: ['240 (financiamento de 20 anos)', '140 (faltam 140 parcelas)'],
    constraints: ['Obrigatório.', 'De 1 a 1200 (100 anos).'],
  },
  first_installment_date: {
    id: 'financing-first_installment_date',
    label: 'Data da 1ª parcela / da próxima parcela',
    description:
      'A partir de qual mês o app começa a gerar vencimentos. O rótulo muda conforme a "Situação do financiamento": data da 1ª parcela do contrato (novo) ou data da próxima parcela a vencer (já em andamento).',
    format: 'Data (dd/mm/aaaa).',
    constraints: [
      'Obrigatória.',
      'Precisa cair no mesmo dia do mês informado em "Dia de vencimento" (ou no último dia do mês, se ele for mais curto que esse dia).',
      'Trava depois do 1º pagamento registrado — para mudar, encerre este financiamento e cadastre um novo.',
    ],
  },
  due_day: {
    id: 'financing-due_day',
    label: 'Dia de vencimento',
    description: 'O dia do mês em que a parcela vence, todo mês.',
    format: 'Número de 1 a 31.',
    examples: ['5', '10'],
    constraints: [
      'Obrigatório.',
      'Em meses mais curtos que esse dia (ex.: dia 31 em abril), o vencimento cai no último dia do mês.',
      'Trava depois do 1º pagamento registrado, junto com a data da 1ª parcela.',
    ],
  },
  is_paid_off: {
    id: 'financing-is_paid_off',
    label: 'Quitado',
    description:
      'Marque quando o financiamento for encerrado. Ele some da dívida (patrimônio líquido) e para de gerar vencimentos/compromissos dali em diante — mas o registro e o histórico de pagamentos continuam existindo.',
    options: [
      {
        value: 'false',
        label: 'Desmarcado',
        effect: 'Entra na dívida e continua gerando vencimentos mensais.',
      },
      {
        value: 'true',
        label: 'Marcado',
        effect: 'Sai da dívida (saldo devedor não conta mais) e para de gerar vencimentos novos.',
      },
    ],
  },
  initial_debt_balance: {
    id: 'financing-initial_debt_balance',
    label: 'Saldo devedor atual (R$)',
    description:
      'Só aparece quando a situação é "Financiamento já em andamento". Copie do extrato do banco. Sem isso, a dívida do imóvel ficaria estimada como o valor financiado total — errado para um contrato que já teve parcelas pagas.',
    format: 'Reais com vírgula decimal.',
    examples: ['180.000,00'],
    constraints: ['Obrigatório quando a situação é "existente".'],
  },
  initial_debt_balance_date: {
    id: 'financing-initial_debt_balance_date',
    label: 'Data do saldo devedor',
    description: 'A data do extrato de onde você tirou o saldo devedor atual.',
    format: 'Data (dd/mm/aaaa).',
    constraints: ['Obrigatória quando a situação é "existente".'],
  },
} as const satisfies Record<string, FieldHelp>

/**
 * Chave = `name` do campo no diálogo avulso "Lançar saldo devedor" (fora do cadastro do
 * financiamento). Mesma entidade (DebtBalance) do `initial_debt_balance*` acima.
 */
export const balanceHelp = {
  balance_date: {
    id: 'financing-balance_date',
    label: 'Data do extrato',
    description: 'A data do extrato de onde você tirou o saldo devedor.',
    format: 'Data (dd/mm/aaaa).',
    constraints: ['Obrigatória.'],
  },
  balance: {
    id: 'financing-balance',
    label: 'Saldo devedor (R$)',
    description:
      'Quanto ainda falta pagar, segundo o extrato do banco. O saldo com a data mais recente é o que conta como a dívida atual do financiamento — lançar um novo saldo não apaga os anteriores, só passa a valer no lugar deles.',
    format: 'Reais com vírgula decimal.',
    examples: ['178.500,00'],
    constraints: ['Obrigatório.'],
  },
} as const satisfies Record<string, FieldHelp>

export const financingSection: HelpSection = {
  id: 'financiamento',
  title: 'Financiamento',
  intro:
    'Um financiamento pertence a um imóvel (um imóvel pode ter zero, um ou vários — ex.: banco + parcelamento com a construtora). A dívida atual do financiamento vem do saldo devedor mais recente lançado; se não houver nenhum, é estimada como o valor financiado total.',
  fields: [...Object.values(financingHelp), ...Object.values(balanceHelp)],
  usageExamples: [
    {
      title: 'Cadastrar um financiamento novo, assinado agora',
      steps: [
        'Na ficha do imóvel, clique em "Novo financiamento".',
        'Deixe a situação em "Novo financiamento".',
        'Preencha credor, valor financiado e parcela atual.',
        'Preencha prazo total (ex.: 240 meses), a data da 1ª parcela e o dia de vencimento (os dois precisam bater).',
        'Salve. Os compromissos do mês passam a mostrar essa parcela a partir do mês da 1ª parcela.',
      ],
    },
    {
      title: 'Cadastrar um financiamento que já está em andamento',
      steps: [
        'Na ficha do imóvel, clique em "Novo financiamento".',
        'Mude a situação para "Financiamento já em andamento".',
        'Preencha credor, valor financiado (o valor original do contrato, mesmo que já tenha pago parte) e parcela atual.',
        'Preencha o prazo restante (quantas parcelas ainda faltam) e a data da próxima parcela a vencer.',
        'Preencha o saldo devedor atual e a data do extrato de onde ele veio.',
        'Salve. O app cria o financiamento e já lança o saldo devedor informado — a dívida aparece correta, não como o valor financiado total.',
      ],
    },
    {
      title: 'Atualizar o saldo devedor de um financiamento existente',
      steps: [
        'Na ficha do imóvel, ache o financiamento e clique em "Lançar saldo".',
        'Preencha a data do extrato e o saldo devedor de hoje.',
        'Salve. A dívida do imóvel passa a usar esse valor (o mais recente lançado), sem apagar o histórico anterior.',
      ],
    },
  ],
}
