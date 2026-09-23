// Seções da ficha do imóvel: avaliações, financiamentos (com saldos), despesas e pagamentos.

import { Plus } from 'lucide-react'
import type { Balance, Expense, Financing, Payment, PropertyDetail, Valuation } from '@/api/types'
import { Money } from '@/components/display'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate, formatDateOrDash } from '@/lib/dates'
import {
  AMORTIZATION_SYSTEM_LABELS,
  EXPENSE_TYPE_LABELS,
  FREQUENCY_LABELS,
  INTEREST_INDEX_LABELS,
  VALUATION_SOURCE_LABELS,
} from '@/lib/labels'
import { formatPercent } from '@/lib/percent'
import { EmptyLine, RowActions, Section } from './common'

export interface SectionHandlers<T> {
  onAdd: () => void
  onEdit: (record: T) => void
  onDelete: (record: T) => void
}

export function ValuationsSection({
  valuations,
  ...handlers
}: { valuations: Valuation[] } & SectionHandlers<Valuation>) {
  return (
    <Section title="Avaliações de mercado" addLabel="Nova avaliação" onAdd={handlers.onAdd}>
      {valuations.length === 0 && (
        <EmptyLine>Sem avaliação: o imóvel aparece como “sem valor”.</EmptyLine>
      )}
      <ul className="grid divide-y">
        {valuations.map((valuation, index) => (
          <li key={valuation.id} className="flex items-center justify-between gap-3 py-2">
            <div className="grid gap-0.5 text-sm">
              <span className="flex items-center gap-2 font-medium">
                <Money cents={valuation.value_cents} />
                {index === 0 && <Badge variant="secondary">Atual</Badge>}
              </span>
              <span className="text-muted-foreground">
                {formatDate(valuation.valuation_date)} · {VALUATION_SOURCE_LABELS[valuation.source]}
              </span>
            </div>
            <RowActions
              itemLabel="avaliação"
              deleteWarning="A avaliação será apagada do histórico."
              onEdit={() => handlers.onEdit(valuation)}
              onDelete={() => handlers.onDelete(valuation)}
            />
          </li>
        ))}
      </ul>
    </Section>
  )
}

interface FinancingHandlers extends SectionHandlers<Financing> {
  onAddBalance: (financing: Financing) => void
  onEditBalance: (financing: Financing, balance: Balance) => void
  onDeleteBalance: (balance: Balance) => void
}

function BalanceList({
  financing,
  handlers,
}: {
  financing: Financing
  handlers: FinancingHandlers
}) {
  return (
    <div className="grid gap-2 rounded-md bg-muted/40 p-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium">Saldos devedores lançados</span>
        <Button size="xs" variant="outline" onClick={() => handlers.onAddBalance(financing)}>
          <Plus className="size-3" />
          Lançar saldo
        </Button>
      </div>
      {financing.balances.length === 0 && (
        <EmptyLine>
          Nenhum saldo lançado: a dívida usa o valor financiado como estimativa.
        </EmptyLine>
      )}
      <ul className="grid divide-y">
        {financing.balances.map((balance) => (
          <li key={balance.id} className="flex items-center justify-between gap-2 py-1 text-sm">
            <span>
              {formatDate(balance.balance_date)} · <Money cents={balance.balance_cents} />
            </span>
            <RowActions
              itemLabel="saldo"
              deleteWarning="O registro de saldo será apagado."
              onEdit={() => handlers.onEditBalance(financing, balance)}
              onDelete={() => handlers.onDeleteBalance(balance)}
            />
          </li>
        ))}
      </ul>
    </div>
  )
}

function FinancingItem({
  financing,
  handlers,
}: {
  financing: Financing
  handlers: FinancingHandlers
}) {
  return (
    <li className="grid gap-3 rounded-lg border p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="grid gap-1 text-sm">
          <span className="flex flex-wrap items-center gap-2 font-medium">
            {financing.lender}
            {financing.is_paid_off && <Badge variant="secondary">Quitado</Badge>}
            {financing.debt_estimated && <Badge variant="outline">Dívida estimada</Badge>}
          </span>
          <span className="text-muted-foreground">
            Parcela <Money cents={financing.current_installment_cents} /> todo dia{' '}
            {financing.due_day} · {financing.term_months} meses desde{' '}
            {formatDate(financing.first_installment_date)}
          </span>
          <span className="text-muted-foreground">
            {AMORTIZATION_SYSTEM_LABELS[financing.amortization_system]} ·{' '}
            {formatPercent(financing.annual_interest_rate)} a.a. +{' '}
            {INTEREST_INDEX_LABELS[financing.interest_index]}
            {financing.contract_number && ` · contrato ${financing.contract_number}`}
          </span>
          <span>
            Dívida atual: <Money cents={financing.current_debt_cents} className="font-medium" />
          </span>
        </div>
        <RowActions
          itemLabel="financiamento"
          deleteWarning="O financiamento, os saldos lançados e os pagamentos das parcelas serão apagados."
          onEdit={() => handlers.onEdit(financing)}
          onDelete={() => handlers.onDelete(financing)}
        />
      </div>
      <BalanceList financing={financing} handlers={handlers} />
    </li>
  )
}

export function FinancingsSection({
  financings,
  ...handlers
}: { financings: Financing[] } & FinancingHandlers) {
  return (
    <Section title="Financiamentos" addLabel="Novo financiamento" onAdd={handlers.onAdd}>
      {financings.length === 0 && <EmptyLine>Nenhum financiamento.</EmptyLine>}
      <ul className="grid gap-3">
        {financings.map((financing) => (
          <FinancingItem key={financing.id} financing={financing} handlers={handlers} />
        ))}
      </ul>
    </Section>
  )
}

function expenseSchedule(expense: Expense): string {
  const parts = [
    `${FREQUENCY_LABELS[expense.frequency]}, dia ${expense.due_day}`,
    `desde ${formatDate(expense.start_date)}`,
  ]
  if (expense.installment_count) parts.push(`${expense.installment_count} parcelas`)
  if (expense.end_date) parts.push(`até ${formatDate(expense.end_date)}`)
  return parts.join(' · ')
}

export function ExpensesSection({
  expenses,
  ...handlers
}: { expenses: Expense[] } & SectionHandlers<Expense>) {
  return (
    <Section title="Despesas recorrentes" addLabel="Nova despesa" onAdd={handlers.onAdd}>
      {expenses.length === 0 && <EmptyLine>Nenhuma despesa cadastrada.</EmptyLine>}
      <ul className="grid divide-y">
        {expenses.map((expense) => (
          <li key={expense.id} className="flex items-start justify-between gap-3 py-2">
            <div className="grid gap-0.5 text-sm">
              <span className="flex flex-wrap items-center gap-2 font-medium">
                {expense.description}
                <Badge variant="outline">{EXPENSE_TYPE_LABELS[expense.expense_type]}</Badge>
                {!expense.is_active && <Badge variant="secondary">Inativa</Badge>}
              </span>
              <span className="text-muted-foreground">
                <Money cents={expense.amount_cents} /> · {expenseSchedule(expense)}
              </span>
            </div>
            <RowActions
              itemLabel="despesa"
              deleteWarning="A despesa e todos os pagamentos dela serão apagados. Para parar de gerar vencimentos mantendo o histórico, use a data de fim."
              onEdit={() => handlers.onEdit(expense)}
              onDelete={() => handlers.onDelete(expense)}
            />
          </li>
        ))}
      </ul>
    </Section>
  )
}

function paymentSource(payment: Payment, property: PropertyDetail): string {
  if (payment.source_kind === 'financing') {
    const financing = property.financings.find((f) => f.id === payment.source_id)
    return financing ? `Parcela — ${financing.lender}` : 'Parcela'
  }
  return property.expenses.find((e) => e.id === payment.source_id)?.description ?? 'Despesa'
}

export function PaymentsSection({
  property,
  onDelete,
}: {
  property: PropertyDetail
  onDelete: (payment: Payment) => void
}) {
  const payments = [...property.payments].reverse()
  return (
    <Section title="Pagamentos">
      {payments.length === 0 && (
        <EmptyLine>Nenhum pagamento. Registre pelos compromissos do mês.</EmptyLine>
      )}
      <ul className="grid divide-y">
        {payments.map((payment) => (
          <li key={payment.id} className="flex items-center justify-between gap-3 py-2 text-sm">
            <div className="grid gap-0.5">
              <span className="font-medium">{paymentSource(payment, property)}</span>
              <span className="text-muted-foreground">
                Vencimento {formatDate(payment.reference_due_date)} · pago em{' '}
                {formatDateOrDash(payment.payment_date)} ·{' '}
                <Money cents={payment.amount_paid_cents} />
              </span>
            </div>
            <RowActions
              itemLabel="pagamento"
              deleteWarning="O vencimento volta a aparecer como a pagar ou atrasado."
              onDelete={() => onDelete(payment)}
            />
          </li>
        ))}
      </ul>
    </Section>
  )
}
