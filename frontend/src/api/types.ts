// Tipos das respostas da API, escritos à mão (STACK_E_PLANO, Fase 3).
// Dinheiro: inteiros em centavos (*_cents). Percentual/taxa: texto decimal. Datas: "AAAA-MM-DD".

import type {
  AcquisitionMethod,
  AmortizationSystem,
  DueStatus,
  ExpenseType,
  Frequency,
  InterestIndex,
  PropertyType,
  PropertyUsage,
  ValuationSource,
} from '@/lib/labels'

export interface User {
  id: number
  email: string
  is_demo: boolean
}

export interface Equity {
  market_value_cents: number | null
  gross_cents: number | null
  debt_cents: number
  net_cents: number | null
  debt_estimated: boolean
}

export interface PropertySummary extends Equity {
  id: number
  nickname: string
  property_type: PropertyType
  usage: PropertyUsage
  is_active: boolean
  ownership_percentage: string
}

export interface PropertyFields {
  nickname: string
  property_type: PropertyType
  usage: PropertyUsage
  street: string | null
  number: string | null
  complement: string | null
  neighborhood: string | null
  city: string | null
  state: string | null
  zip_code: string | null
  registration_number: string | null
  registry_office: string | null
  municipal_registration: string | null
  ownership_percentage: string
  acquisition_date: string | null
  acquisition_method: AcquisitionMethod | null
  purchase_price_cents: number
  itbi_cents: number
  deed_registration_cents: number
  is_active: boolean
}

export interface Valuation {
  id: number
  property_id: number
  valuation_date: string
  value_cents: number
  source: ValuationSource
}

export interface Balance {
  id: number
  financing_id: number
  balance_date: string
  balance_cents: number
}

export interface FinancingFields {
  lender: string
  contract_number: string | null
  financed_amount_cents: number
  amortization_system: AmortizationSystem
  annual_interest_rate: string
  interest_index: InterestIndex
  term_months: number
  first_installment_date: string
  due_day: number
  current_installment_cents: number
  is_paid_off: boolean
}

export interface Financing extends FinancingFields {
  id: number
  property_id: number
  current_debt_cents: number
  debt_estimated: boolean
  has_payments: boolean
  balances: Balance[]
}

export interface ExpenseFields {
  expense_type: ExpenseType
  description: string
  amount_cents: number
  frequency: Frequency
  due_day: number
  start_date: string
  end_date: string | null
  installment_count: number | null
  is_active: boolean
}

export interface Expense extends ExpenseFields {
  id: number
  property_id: number
  has_payments: boolean
}

export type SourceKind = 'recurring_expense' | 'financing'

export interface Payment {
  id: number
  source_kind: SourceKind
  source_id: number
  reference_due_date: string
  payment_date: string
  amount_paid_cents: number
}

export interface PropertyDetail extends PropertySummary, PropertyFields {
  acquisition_total_cents: number
  valuations: Valuation[]
  financings: Financing[]
  expenses: Expense[]
  payments: Payment[]
}

export interface Dashboard {
  gross_total_cents: number
  debt_total_cents: number
  net_total_cents: number
  property_count: number
  count_by_type: Partial<Record<PropertyType, number>>
  properties_without_value: number
  debt_estimated: boolean
}

export interface DueItem {
  source_kind: SourceKind
  source_id: number
  property_id: number
  property_nickname: string
  description: string
  due_date: string
  expected_amount_cents: number
  status: DueStatus
  amount_paid_cents: number | null
  payment_id: number | null
}

export interface DueTotals {
  items: DueItem[]
  total_expected_cents: number
  total_paid_cents: number
  total_open_cents: number
  total_overdue_cents: number
}

export interface Commitments extends DueTotals {
  year: number
  month: number
  today: string
}

export interface ErrorDetail {
  field: string | null
  type: string
  message: string
}

export interface ErrorBody {
  error: string
  message?: string
  details?: ErrorDetail[]
  fields?: string[]
}
