// Esquemas e conversões dos formulários da ficha: avaliação, financiamento, saldo e despesa.

import { z } from 'zod'
import type { BalanceFields, ValuationFields } from '@/api/queries'
import type {
  Balance,
  Expense,
  ExpenseFields,
  Financing,
  FinancingFields,
  Valuation,
} from '@/api/types'
import {
  emptyToNull,
  enumText,
  integerText,
  optionalDate,
  optionalMoney,
  optionalText,
  percentText,
  requiredDate,
  requiredMoney,
  requiredText,
  toCents,
  toOptionalInt,
  toPercent,
} from '@/lib/formFields'
import {
  AMORTIZATION_SYSTEM_LABELS,
  type AmortizationSystem,
  EXPENSE_TYPE_LABELS,
  type ExpenseType,
  FREQUENCY_LABELS,
  type Frequency,
  INTEREST_INDEX_LABELS,
  type InterestIndex,
  VALUATION_SOURCE_LABELS,
  type ValuationSource,
} from '@/lib/labels'
import { centsToInput } from '@/lib/money'
import { apiPercentToInput } from '@/lib/percent'

// --- avaliação ---

export const valuationSchema = z.object({
  valuation_date: requiredDate,
  value: requiredMoney,
  source: enumText(VALUATION_SOURCE_LABELS),
})
export type ValuationFormValues = z.infer<typeof valuationSchema>

export function valuationToForm(valuation?: Valuation): ValuationFormValues {
  if (!valuation) return { valuation_date: '', value: '', source: '' }
  return {
    valuation_date: valuation.valuation_date,
    value: centsToInput(valuation.value_cents),
    source: valuation.source,
  }
}

export function formToValuation(values: ValuationFormValues): ValuationFields {
  return {
    valuation_date: values.valuation_date,
    value_cents: toCents(values.value),
    source: values.source as ValuationSource,
  }
}

// --- saldo devedor ---

export const balanceSchema = z.object({ balance_date: requiredDate, balance: requiredMoney })
export type BalanceFormValues = z.infer<typeof balanceSchema>

export function balanceToForm(balance?: Balance): BalanceFormValues {
  if (!balance) return { balance_date: '', balance: '' }
  return { balance_date: balance.balance_date, balance: centsToInput(balance.balance_cents) }
}

export function formToBalance(values: BalanceFormValues): BalanceFields {
  return { balance_date: values.balance_date, balance_cents: toCents(values.balance) }
}

// --- financiamento ---

/** Modo de cadastro: só decide quais campos o formulário pede, nada é gravado à parte. */
export const FINANCING_MODE_LABELS = {
  novo: 'Novo financiamento',
  existente: 'Financiamento já em andamento',
} as const
export type FinancingMode = keyof typeof FINANCING_MODE_LABELS

export const financingSchema = z
  .object({
    mode: enumText(FINANCING_MODE_LABELS),
    lender: requiredText(100),
    contract_number: optionalText(50),
    financed_amount: requiredMoney,
    amortization_system: enumText(AMORTIZATION_SYSTEM_LABELS),
    annual_interest_rate: percentText(1000),
    interest_index: enumText(INTEREST_INDEX_LABELS),
    term_months: integerText(1, 1200),
    first_installment_date: requiredDate,
    due_day: integerText(1, 31),
    current_installment: requiredMoney,
    is_paid_off: z.boolean(),
    initial_debt_balance: optionalMoney,
    initial_debt_balance_date: optionalDate,
  })
  .refine(
    (values) =>
      values.mode !== 'existente' ||
      (values.initial_debt_balance.trim() !== '' && values.initial_debt_balance_date.trim() !== ''),
    {
      message:
        'Informe o saldo devedor atual (sem ele, a dívida aparece como o valor financiado total).',
      path: ['initial_debt_balance'],
    },
  )
export type FinancingFormValues = z.infer<typeof financingSchema>

export function financingToForm(financing?: Financing): FinancingFormValues {
  if (!financing) {
    return {
      mode: 'novo',
      lender: '',
      contract_number: '',
      financed_amount: '',
      amortization_system: '',
      annual_interest_rate: '',
      interest_index: '',
      term_months: '',
      first_installment_date: '',
      due_day: '',
      current_installment: '',
      is_paid_off: false,
      initial_debt_balance: '',
      initial_debt_balance_date: '',
    }
  }
  return {
    mode: 'novo',
    lender: financing.lender,
    contract_number: financing.contract_number ?? '',
    financed_amount: centsToInput(financing.financed_amount_cents),
    amortization_system: financing.amortization_system,
    annual_interest_rate: apiPercentToInput(financing.annual_interest_rate),
    interest_index: financing.interest_index,
    term_months: String(financing.term_months),
    first_installment_date: financing.first_installment_date,
    due_day: String(financing.due_day),
    current_installment: centsToInput(financing.current_installment_cents),
    is_paid_off: financing.is_paid_off,
    initial_debt_balance: '',
    initial_debt_balance_date: '',
  }
}

export function formToFinancing(values: FinancingFormValues): FinancingFields {
  return {
    lender: values.lender.trim(),
    contract_number: emptyToNull(values.contract_number),
    financed_amount_cents: toCents(values.financed_amount),
    amortization_system: values.amortization_system as AmortizationSystem,
    annual_interest_rate: toPercent(values.annual_interest_rate, 1000),
    interest_index: values.interest_index as InterestIndex,
    term_months: Number(values.term_months),
    first_installment_date: values.first_installment_date,
    due_day: Number(values.due_day),
    current_installment_cents: toCents(values.current_installment),
    is_paid_off: values.is_paid_off,
  }
}

// --- despesa recorrente ---

export const expenseSchema = z
  .object({
    expense_type: enumText(EXPENSE_TYPE_LABELS),
    description: requiredText(200),
    amount: requiredMoney,
    frequency: enumText(FREQUENCY_LABELS),
    due_day: integerText(1, 31),
    start_date: requiredDate,
    end_date: optionalDate,
    installment_count: integerText(1, 1200, true),
    is_active: z.boolean(),
  })
  .refine((values) => values.end_date === '' || values.end_date >= values.start_date, {
    message: 'A data de fim não pode ser anterior à de início.',
    path: ['end_date'],
  })
export type ExpenseFormValues = z.infer<typeof expenseSchema>

export function expenseToForm(expense?: Expense): ExpenseFormValues {
  if (!expense) {
    return {
      expense_type: '',
      description: '',
      amount: '',
      frequency: 'mensal',
      due_day: '',
      start_date: '',
      end_date: '',
      installment_count: '',
      is_active: true,
    }
  }
  return {
    expense_type: expense.expense_type,
    description: expense.description,
    amount: centsToInput(expense.amount_cents),
    frequency: expense.frequency,
    due_day: String(expense.due_day),
    start_date: expense.start_date,
    end_date: expense.end_date ?? '',
    installment_count: expense.installment_count === null ? '' : String(expense.installment_count),
    is_active: expense.is_active,
  }
}

export function formToExpense(values: ExpenseFormValues): ExpenseFields {
  return {
    expense_type: values.expense_type as ExpenseType,
    description: values.description.trim(),
    amount_cents: toCents(values.amount),
    frequency: values.frequency as Frequency,
    due_day: Number(values.due_day),
    start_date: values.start_date,
    end_date: emptyToNull(values.end_date),
    installment_count: toOptionalInt(values.installment_count),
    is_active: values.is_active,
  }
}
