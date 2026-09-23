// Valores dos enums da API (ESCOPO_IMOVEIS.md) -> textos da interface.

export const PROPERTY_TYPE_LABELS = {
  casa: 'Casa',
  casa_condominio: 'Casa em condomínio',
  apartamento: 'Apartamento',
  terreno: 'Terreno',
  terreno_condominio: 'Terreno em condomínio',
  sala_comercial: 'Sala comercial',
  loja: 'Loja',
  galpao: 'Galpão',
  predio: 'Prédio',
  chacara_sitio: 'Chácara / sítio',
  fazenda: 'Fazenda',
  vaga_garagem: 'Vaga de garagem',
  box: 'Box',
  outro: 'Outro',
} as const

export const PROPERTY_USAGE_LABELS = {
  moradia_propria: 'Moradia própria',
  alugado: 'Alugado',
  vazio: 'Vazio',
  comercial_proprio: 'Comercial próprio',
  em_construcao: 'Em construção',
} as const

export const ACQUISITION_METHOD_LABELS = {
  compra: 'Compra',
  heranca: 'Herança',
  doacao: 'Doação',
  construcao: 'Construção',
  outro: 'Outro',
} as const

export const VALUATION_SOURCE_LABELS = {
  estimativa_propria: 'Estimativa própria',
  corretor: 'Corretor',
  laudo: 'Laudo',
  anuncio_similar: 'Anúncio similar',
  outro: 'Outro',
} as const

export const AMORTIZATION_SYSTEM_LABELS = {
  sac: 'SAC',
  price: 'Price',
  outro: 'Outro',
} as const

export const INTEREST_INDEX_LABELS = {
  tr: 'TR',
  ipca: 'IPCA',
  prefixado: 'Prefixado',
  outro: 'Outro',
} as const

export const EXPENSE_TYPE_LABELS = {
  iptu: 'IPTU',
  condominio: 'Condomínio',
  cota_extra: 'Cota extra',
  seguro: 'Seguro',
  agua: 'Água',
  luz: 'Luz',
  gas: 'Gás',
  internet: 'Internet',
  taxa_lixo: 'Taxa de lixo',
  itr: 'ITR',
  laudemio_foro: 'Laudêmio / foro',
  manutencao: 'Manutenção',
  outro: 'Outro',
} as const

export const FREQUENCY_LABELS = {
  mensal: 'Mensal',
  bimestral: 'Bimestral',
  trimestral: 'Trimestral',
  semestral: 'Semestral',
  anual: 'Anual',
  unica: 'Única',
} as const

export const DUE_STATUS_LABELS = {
  pago: 'Pago',
  a_pagar: 'A pagar',
  atrasado: 'Atrasado',
} as const

export type PropertyType = keyof typeof PROPERTY_TYPE_LABELS
export type PropertyUsage = keyof typeof PROPERTY_USAGE_LABELS
export type AcquisitionMethod = keyof typeof ACQUISITION_METHOD_LABELS
export type ValuationSource = keyof typeof VALUATION_SOURCE_LABELS
export type AmortizationSystem = keyof typeof AMORTIZATION_SYSTEM_LABELS
export type InterestIndex = keyof typeof INTEREST_INDEX_LABELS
export type ExpenseType = keyof typeof EXPENSE_TYPE_LABELS
export type Frequency = keyof typeof FREQUENCY_LABELS
export type DueStatus = keyof typeof DUE_STATUS_LABELS

/** Opções para selects, na ordem do ESCOPO. */
export function optionsOf<K extends string>(
  labels: Record<K, string>,
): { value: K; label: string }[] {
  return (Object.keys(labels) as K[]).map((value) => ({ value, label: labels[value] }))
}
