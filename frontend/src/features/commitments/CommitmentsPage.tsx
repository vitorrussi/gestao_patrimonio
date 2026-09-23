// Compromissos do mês: tudo que vence no mês, com status, totais e registro de pagamento.
// O mês escolhido fica na URL (?mes=2026-09), então dá para voltar e compartilhar o link.

import { ChevronLeft, ChevronRight, Undo2 } from 'lucide-react'
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { toast } from 'sonner'
import { useCommitments, useDeleteRecord } from '@/api/queries'
import type { Commitments, DueItem } from '@/api/types'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import {
  EmptyState,
  LoadingState,
  Money,
  PageHeader,
  QueryErrorState,
  StatusBadge,
} from '@/components/display'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { errorMessage } from '@/lib/apiErrors'
import { type YearMonth, addMonths, formatDate, formatMonth } from '@/lib/dates'
import { PaymentDialog } from './PaymentDialog'

function parseMonthParam(value: string | null): YearMonth | null {
  const match = value ? /^(\d{4})-(\d{2})$/.exec(value) : null
  if (!match) return null
  const month = Number(match[2])
  return month >= 1 && month <= 12 ? { year: Number(match[1]), month } : null
}

function toMonthParam({ year, month }: YearMonth): string {
  return `${year}-${String(month).padStart(2, '0')}`
}

function MonthNavigator({
  period,
  onChange,
}: {
  period: YearMonth
  onChange: (p: YearMonth) => void
}) {
  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="icon"
        aria-label="Mês anterior"
        onClick={() => onChange(addMonths(period, -1))}
      >
        <ChevronLeft className="size-4" />
      </Button>
      <span className="inline-block min-w-40 text-center font-medium first-letter:uppercase">
        {formatMonth(period)}
      </span>
      <Button
        variant="outline"
        size="icon"
        aria-label="Próximo mês"
        onClick={() => onChange(addMonths(period, 1))}
      >
        <ChevronRight className="size-4" />
      </Button>
    </div>
  )
}

function Totals({ data }: { data: Commitments }) {
  const cards = [
    { title: 'Previsto no mês', cents: data.total_expected_cents },
    { title: 'Pago', cents: data.total_paid_cents },
    { title: 'Em aberto', cents: data.total_open_cents },
    { title: 'Atrasado', cents: data.total_overdue_cents },
  ]
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title} size="sm">
          <CardHeader>
            <CardDescription>{card.title}</CardDescription>
            <CardTitle className="text-lg">
              <Money cents={card.cents} />
            </CardTitle>
          </CardHeader>
        </Card>
      ))}
    </div>
  )
}

interface ItemActionsProps {
  item: DueItem
  onPay: (item: DueItem) => void
  onUndo: (paymentId: number) => void
}

function ItemActions({ item, onPay, onUndo }: ItemActionsProps) {
  if (item.payment_id === null) {
    return (
      <Button size="sm" onClick={() => onPay(item)}>
        Registrar pagamento
      </Button>
    )
  }
  const paymentId = item.payment_id
  return (
    <ConfirmDialog
      title="Desfazer o pagamento?"
      description="O vencimento volta a aparecer como a pagar ou atrasado."
      confirmLabel="Desfazer"
      onConfirm={() => onUndo(paymentId)}
      trigger={
        <Button size="sm" variant="ghost">
          <Undo2 className="size-4" />
          Desfazer
        </Button>
      }
    />
  )
}

function DueList({ items, onPay, onUndo }: { items: DueItem[] } & Omit<ItemActionsProps, 'item'>) {
  return (
    <ul className="grid divide-y rounded-lg border">
      {items.map((item) => (
        <li
          key={`${item.source_kind}-${item.source_id}-${item.due_date}`}
          className="flex flex-col gap-3 p-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="grid gap-1 text-sm">
            <span className="flex flex-wrap items-center gap-2 font-medium">
              {item.description}
              <StatusBadge status={item.status} />
            </span>
            <span className="text-muted-foreground">
              <Link to={`/imoveis/${item.property_id}`} className="hover:underline">
                {item.property_nickname}
              </Link>{' '}
              · vence {formatDate(item.due_date)}
            </span>
          </div>
          <div className="flex items-center justify-between gap-3 sm:justify-end">
            <div className="grid text-right text-sm">
              <Money cents={item.expected_amount_cents} className="font-medium" />
              {item.amount_paid_cents !== null &&
                item.amount_paid_cents !== item.expected_amount_cents && (
                  <span className="text-xs text-muted-foreground">
                    pago <Money cents={item.amount_paid_cents} />
                  </span>
                )}
            </div>
            <ItemActions item={item} onPay={onPay} onUndo={onUndo} />
          </div>
        </li>
      ))}
    </ul>
  )
}

export function CommitmentsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const requested = parseMonthParam(searchParams.get('mes'))
  const commitments = useCommitments(requested)
  const [paying, setPaying] = useState<DueItem | null>(null)
  const deleteRecord = useDeleteRecord()

  const undo = (paymentId: number) =>
    deleteRecord.mutate(
      { kind: 'payments', id: paymentId },
      {
        onSuccess: () => toast.success('Pagamento desfeito.'),
        onError: (error) => toast.error(errorMessage(error)),
      },
    )

  if (commitments.isPending) return <LoadingState />
  if (commitments.isError) {
    return <QueryErrorState error={commitments.error} onRetry={() => void commitments.refetch()} />
  }
  const data = commitments.data
  const period = { year: data.year, month: data.month }

  return (
    <>
      <PageHeader
        title="Compromissos do mês"
        description="Despesas e parcelas que vencem no mês, com o que já foi pago."
        actions={
          <MonthNavigator
            period={period}
            onChange={(p) => setSearchParams({ mes: toMonthParam(p) })}
          />
        }
      />
      <Totals data={data} />
      {data.items.length === 0 ? (
        <EmptyState message="Nada vence neste mês." />
      ) : (
        <DueList items={data.items} onPay={setPaying} onUndo={undo} />
      )}
      {paying && <PaymentDialog item={paying} today={data.today} onClose={() => setPaying(null)} />}
    </>
  )
}
