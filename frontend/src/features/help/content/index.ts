// Agrega o conteúdo de ajuda de cada entidade (um arquivo por entidade nesta pasta),
// para a página /ajuda listar todas as seções. Os diálogos de formulário importam
// direto o `*Help` da entidade que usam (ex.: `content/financing`).

import type { HelpSection } from '../types'
import { balanceHelp, financingHelp, financingSection } from './financing'
import { expenseHelp, expenseSection } from './expense'
import { propertyHelp, propertySection } from './property'
import { valuationHelp, valuationSection } from './valuation'

export const helpSections: HelpSection[] = [
  propertySection,
  valuationSection,
  financingSection,
  expenseSection,
]

export { balanceHelp, expenseHelp, financingHelp, propertyHelp, valuationHelp }
export type { FieldHelp, FieldOption, HelpSection, UsageExample } from '../types'
