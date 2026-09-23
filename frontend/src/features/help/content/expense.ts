import type { FieldHelp, HelpSection } from '../types'

/** Chave = `name` do campo no formulário de despesa recorrente (`ExpenseFormValues`). */
export const expenseHelp = {
  expense_type: {
    id: 'expense-expense_type',
    label: 'Tipo',
    description:
      'A categoria da despesa. Só para organização (aparece nos compromissos e, numa fase futura, no custo anual por imóvel); nenhum tipo muda como o vencimento é calculado.',
    format:
      'Lista fixa: IPTU, condomínio, cota extra, seguro, água, luz, gás, internet, taxa de lixo, ITR, laudêmio/foro (terrenos de marinha ou enfitêuticos), manutenção ou outro.',
    constraints: ['Obrigatório.'],
  },
  description: {
    id: 'expense-description',
    label: 'Descrição',
    description: 'Um texto livre para você identificar a despesa nas telas do app.',
    format: 'Texto livre, até 200 caracteres.',
    examples: ['IPTU 2026 — parcelado em 10x', 'Condomínio'],
    constraints: ['Obrigatório.'],
  },
  amount: {
    id: 'expense-amount',
    label: 'Valor de cada vencimento (R$)',
    description: 'Quanto vence a cada ocorrência (não é o total, se for parcelada).',
    format: 'Reais com vírgula decimal.',
    examples: ['450,00'],
    constraints: ['Obrigatório.'],
  },
  frequency: {
    id: 'expense-frequency',
    label: 'Periodicidade',
    description: 'De quanto em quanto tempo a despesa vence.',
    options: [
      { value: 'mensal', label: 'Mensal', effect: 'Um vencimento por mês.' },
      { value: 'bimestral', label: 'Bimestral', effect: 'Um vencimento a cada 2 meses.' },
      { value: 'trimestral', label: 'Trimestral', effect: 'Um vencimento a cada 3 meses.' },
      { value: 'semestral', label: 'Semestral', effect: 'Um vencimento a cada 6 meses.' },
      { value: 'anual', label: 'Anual', effect: 'Um vencimento a cada 12 meses.' },
      {
        value: 'unica',
        label: 'Única',
        effect: 'Só 1 vencimento no total — ignora o que estiver em "Nº de parcelas".',
      },
    ],
  },
  due_day: {
    id: 'expense-due_day',
    label: 'Dia de vencimento',
    description: 'O dia do mês em que cada ocorrência vence.',
    format: 'Número de 1 a 31.',
    examples: ['10'],
    constraints: [
      'Obrigatório.',
      'Em meses mais curtos que esse dia (ex.: dia 31 em abril), o vencimento cai no último dia do mês.',
      'Trava depois do 1º pagamento registrado — para mudar, encerre esta despesa e cadastre uma nova.',
    ],
  },
  start_date: {
    id: 'expense-start_date',
    label: 'Início',
    description:
      'A partir de quando a despesa passa a valer. O primeiro vencimento gerado é o "Dia de vencimento" do mês desta data (ou do mês seguinte, se esse dia já tiver passado dentro do mês da data de início).',
    format: 'Data (dd/mm/aaaa).',
    constraints: [
      'Obrigatória.',
      'Trava depois do 1º pagamento registrado, junto com o dia de vencimento.',
    ],
  },
  installment_count: {
    id: 'expense-installment_count',
    label: 'Nº de parcelas (opcional)',
    description:
      'Quantas ocorrências gerar no total, a partir do início. Deixe em branco para uma despesa sem fim definido (ex.: condomínio) — nesse caso, ela só para de gerar vencimento quando você desmarcar "Ativa" ou preencher "Data de fim". Não tem efeito quando a periodicidade é "Única" (que já é sempre 1 vencimento).',
    format: 'Número inteiro de parcelas.',
    examples: ['10 (IPTU parcelado em 10x)'],
    constraints: ['Opcional.', 'De 1 a 1200 quando preenchido.'],
  },
  end_date: {
    id: 'expense-end_date',
    label: 'Data de fim (opcional)',
    description:
      'Use para encerrar a despesa numa data certa, mantendo os vencimentos e pagamentos anteriores no histórico. Nenhum vencimento é gerado depois dessa data, mesmo que "Nº de parcelas" ainda não tenha se esgotado.',
    format: 'Data (dd/mm/aaaa).',
    constraints: ['Opcional.', 'Não pode ser anterior à data de início.'],
  },
  is_active: {
    id: 'expense-is_active',
    label: 'Ativa',
    description:
      'Desmarque para parar de gerar vencimentos novos sem apagar a despesa nem seu histórico — diferente da "Data de fim", que trava numa data específica.',
    options: [
      {
        value: 'true',
        label: 'Marcada (ativa)',
        effect: 'Continua gerando vencimentos normalmente.',
      },
      {
        value: 'false',
        label: 'Desmarcada',
        effect: 'Para de gerar vencimentos novos a partir de agora.',
      },
    ],
  },
} as const satisfies Record<string, FieldHelp>

export const expenseSection: HelpSection = {
  id: 'despesa',
  title: 'Despesa recorrente',
  intro:
    'Estrutura genérica para tudo que se paga periodicamente num imóvel (IPTU, condomínio, seguro, água, luz etc.). Os vencimentos são calculados na hora a partir destas regras — não ficam gravados um a um no banco.',
  fields: Object.values(expenseHelp),
  usageExamples: [
    {
      title: 'Cadastrar o condomínio (sem fim definido)',
      steps: [
        'Na ficha do imóvel, clique em "Nova despesa".',
        'Tipo: Condomínio. Descrição: algo como "Condomínio".',
        'Preencha o valor de cada vencimento, periodicidade Mensal e o dia de vencimento.',
        'Preencha a data de início e deixe "Nº de parcelas" e "Data de fim" em branco.',
        'Salve. O condomínio passa a aparecer todo mês nos compromissos, indefinidamente.',
      ],
    },
    {
      title: 'Cadastrar o IPTU parcelado em 10x',
      steps: [
        'Na ficha do imóvel, clique em "Nova despesa".',
        'Tipo: IPTU. Descrição: "IPTU 2026 — parcelado em 10x".',
        'Valor de cada vencimento: o valor de cada parcela do carnê.',
        'Periodicidade: Mensal. Nº de parcelas: 10.',
        'Dia de vencimento e data de início: conforme o carnê.',
        'Salve. Isso gera exatamente 10 vencimentos, um por mês.',
      ],
    },
  ],
}
