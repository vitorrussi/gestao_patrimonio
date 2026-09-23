import type { FieldHelp, HelpSection } from '../types'

/** Chave = `name` do campo no formulário de avaliação de mercado (`ValuationFormValues`). */
export const valuationHelp = {
  valuation_date: {
    id: 'valuation-valuation_date',
    label: 'Data',
    description:
      'A data da avaliação. O valor de mercado "atual" do imóvel é sempre o da avaliação com a data mais recente — não o último que você cadastrou, se cadastrar fora de ordem.',
    format: 'Data (dd/mm/aaaa).',
    constraints: ['Obrigatória.'],
  },
  value: {
    id: 'valuation-value',
    label: 'Valor (R$)',
    description:
      'Quanto o imóvel inteiro (100%) vale nessa avaliação. Entra no patrimônio bruto e líquido multiplicado pela sua % de participação no imóvel.',
    format: 'Reais com vírgula decimal.',
    examples: ['450.000,00'],
    constraints: ['Obrigatório.'],
  },
  source: {
    id: 'valuation-source',
    label: 'Fonte',
    description:
      'De onde veio o valor. Só para você lembrar a confiabilidade da estimativa — todas as opções entram no cálculo do mesmo jeito, nenhuma pesa mais que outra.',
    options: [
      {
        value: 'estimativa_propria',
        label: 'Estimativa própria',
        effect: 'Seu próprio chute/cálculo.',
      },
      {
        value: 'corretor',
        label: 'Corretor',
        effect: 'Avaliação verbal ou informal de um corretor.',
      },
      {
        value: 'laudo',
        label: 'Laudo',
        effect: 'Laudo de avaliação formal (ex.: para financiamento ou inventário).',
      },
      {
        value: 'anuncio_similar',
        label: 'Anúncio similar',
        effect: 'Baseado em anúncios de imóveis parecidos na região.',
      },
      { value: 'outro', label: 'Outro', effect: 'Qualquer outra origem.' },
    ],
  },
} as const satisfies Record<string, FieldHelp>

export const valuationSection: HelpSection = {
  id: 'avaliacao',
  title: 'Avaliação de mercado',
  intro:
    'Histórico de quanto o imóvel vale — cada avaliação é um registro novo, nunca sobrescreve a anterior. O valor "atual" usado no painel geral e no patrimônio líquido é sempre o da avaliação mais recente por data.',
  fields: Object.values(valuationHelp),
  usageExamples: [
    {
      title: 'Atualizar o valor de mercado do imóvel',
      steps: [
        'Na ficha do imóvel, clique em "Nova avaliação".',
        'Preencha a data de hoje (ou do laudo/anúncio que você está usando), o valor e a fonte.',
        'Salve. Se essa for a data mais recente entre as avaliações do imóvel, o painel geral já passa a usar esse valor.',
      ],
    },
  ],
}
