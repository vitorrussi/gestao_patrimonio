// Tipos do conteúdo de ajuda (o "?" dos campos e a página /ajuda). Um arquivo por
// entidade em `content/`, agregados em `content/index.ts`.

export interface FieldOption {
  value: string
  label: string
  /** Como essa opção afeta os cálculos do app hoje (ou por que não afeta nenhum). */
  effect: string
}

export interface FieldHelp {
  /** Único no app inteiro: também é o id da âncora em /ajuda (#id). */
  id: string
  label: string
  description: string
  format?: string
  examples?: string[]
  constraints?: string[]
  options?: FieldOption[]
}

export interface UsageExample {
  title: string
  steps: string[]
}

export interface HelpSection {
  id: string
  title: string
  intro: string
  fields: FieldHelp[]
  usageExamples: UsageExample[]
}
