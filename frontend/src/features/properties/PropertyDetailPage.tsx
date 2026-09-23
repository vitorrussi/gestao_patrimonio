// Ficha do imóvel: dados, valores, financiamentos, despesas e pagamentos num lugar só.

import { Pencil, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { toast } from 'sonner'
import { type RecordKind, useDeleteProperty, useDeleteRecord, useProperty } from '@/api/queries'
import type { Balance, Expense, Financing, PropertyDetail, Valuation } from '@/api/types'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { LoadingState, Money, PageHeader, QueryErrorState } from '@/components/display'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { errorMessage } from '@/lib/apiErrors'
import { formatDateOrDash } from '@/lib/dates'
import {
  ACQUISITION_METHOD_LABELS,
  PROPERTY_TYPE_LABELS,
  PROPERTY_USAGE_LABELS,
} from '@/lib/labels'
import { formatPercent } from '@/lib/percent'
import {
  ExpensesSection,
  FinancingsSection,
  PaymentsSection,
  ValuationsSection,
} from './detail/Sections'
import { ExpenseDialog } from './forms/ExpenseDialog'
import { FinancingDialog } from './forms/FinancingDialog'
import { BalanceDialog, ValuationDialog } from './forms/SimpleRecordDialogs'

type OpenDialog =
  | { kind: 'valuation'; record?: Valuation }
  | { kind: 'financing'; record?: Financing }
  | { kind: 'balance'; financingId: number; record?: Balance }
  | { kind: 'expense'; record?: Expense }

function SummaryCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card size="sm">
      <CardHeader>
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-lg">{children}</CardTitle>
      </CardHeader>
    </Card>
  )
}

function Summary({ property }: { property: PropertyDetail }) {
  const noValue = <span className="text-muted-foreground">Sem valor</span>
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      <SummaryCard title="Valor de mercado atual">
        {property.market_value_cents === null ? (
          noValue
        ) : (
          <Money cents={property.market_value_cents} />
        )}
      </SummaryCard>
      <SummaryCard title={`Sua parte (${formatPercent(property.ownership_percentage)})`}>
        {property.gross_cents === null ? noValue : <Money cents={property.gross_cents} />}
      </SummaryCard>
      <SummaryCard title={property.debt_estimated ? 'Saldo devedor (estimado)' : 'Saldo devedor'}>
        <Money cents={property.debt_cents} />
      </SummaryCard>
      <SummaryCard title="Patrimônio líquido">
        {property.net_cents === null ? noValue : <Money cents={property.net_cents} />}
      </SummaryCard>
      <SummaryCard title="Valor total de aquisição">
        <Money cents={property.acquisition_total_cents} />
      </SummaryCard>
    </div>
  )
}

function DataItem({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="grid gap-0.5">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="text-sm">{value || '—'}</dd>
    </div>
  )
}

function address(p: PropertyDetail): string {
  const street = [p.street, p.number, p.complement].filter(Boolean).join(', ')
  const city = [p.neighborhood, p.city && p.state ? `${p.city}/${p.state}` : p.city]
    .filter(Boolean)
    .join(' · ')
  return [street, city, p.zip_code].filter(Boolean).join(' · ')
}

function DataCard({ property }: { property: PropertyDetail }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Dados do imóvel</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <DataItem label="Endereço" value={address(property)} />
          <DataItem
            label="Matrícula / cartório"
            value={[property.registration_number, property.registry_office]
              .filter(Boolean)
              .join(' · ')}
          />
          <DataItem label="Inscrição imobiliária" value={property.municipal_registration} />
          <DataItem label="Data de aquisição" value={formatDateOrDash(property.acquisition_date)} />
          <DataItem
            label="Forma de aquisição"
            value={
              property.acquisition_method && ACQUISITION_METHOD_LABELS[property.acquisition_method]
            }
          />
          <DataItem
            label="Compra · ITBI · escritura"
            value={
              <>
                <Money cents={property.purchase_price_cents} /> ·{' '}
                <Money cents={property.itbi_cents} /> ·{' '}
                <Money cents={property.deed_registration_cents} />
              </>
            }
          />
        </dl>
      </CardContent>
    </Card>
  )
}

function RecordDialogs({
  dialog,
  propertyId,
  onClose,
}: {
  dialog: OpenDialog | null
  propertyId: number
  onClose: () => void
}) {
  switch (dialog?.kind) {
    case 'valuation':
      return <ValuationDialog propertyId={propertyId} valuation={dialog.record} onClose={onClose} />
    case 'financing':
      return <FinancingDialog propertyId={propertyId} financing={dialog.record} onClose={onClose} />
    case 'balance':
      return (
        <BalanceDialog financingId={dialog.financingId} balance={dialog.record} onClose={onClose} />
      )
    case 'expense':
      return <ExpenseDialog propertyId={propertyId} expense={dialog.record} onClose={onClose} />
    default:
      return null
  }
}

function useDeleteWithToast() {
  const deleteRecord = useDeleteRecord()
  return (kind: RecordKind, id: number) =>
    deleteRecord.mutate(
      { kind, id },
      {
        onSuccess: () => toast.success('Excluído.'),
        onError: (error) => toast.error(errorMessage(error)),
      },
    )
}

function Header({ property }: { property: PropertyDetail }) {
  const deleteProperty = useDeleteProperty()
  const navigate = useNavigate()
  const onDelete = () =>
    deleteProperty.mutate(property.id, {
      onSuccess: () => {
        toast.success('Imóvel excluído.')
        void navigate('/imoveis', { replace: true })
      },
      onError: (error) => toast.error(errorMessage(error)),
    })

  return (
    <PageHeader
      title={property.nickname}
      description={
        <span className="flex flex-wrap items-center gap-2">
          {PROPERTY_TYPE_LABELS[property.property_type]} · {PROPERTY_USAGE_LABELS[property.usage]}
          {!property.is_active && <Badge variant="outline">Vendido / inativo</Badge>}
        </span>
      }
      actions={
        <>
          <Button variant="outline" asChild>
            <Link to={`/imoveis/${property.id}/editar`}>
              <Pencil className="size-4" />
              Editar
            </Link>
          </Button>
          <ConfirmDialog
            title="Excluir o imóvel?"
            description="Apaga o imóvel e tudo ligado a ele: avaliações, financiamentos, despesas e pagamentos. Para só tirá-lo dos totais, edite e desmarque “Imóvel ativo”."
            onConfirm={onDelete}
            trigger={
              <Button variant="destructive">
                <Trash2 className="size-4" />
                Excluir
              </Button>
            }
          />
        </>
      }
    />
  )
}

export function PropertyDetailPage() {
  const id = Number(useParams().id)
  const property = useProperty(id)
  const [dialog, setDialog] = useState<OpenDialog | null>(null)
  const remove = useDeleteWithToast()

  if (property.isPending) return <LoadingState />
  if (property.isError) {
    return <QueryErrorState error={property.error} onRetry={() => void property.refetch()} />
  }
  const data = property.data

  return (
    <>
      <Header property={data} />
      <Summary property={data} />
      <DataCard property={data} />
      <ValuationsSection
        valuations={data.valuations}
        onAdd={() => setDialog({ kind: 'valuation' })}
        onEdit={(record) => setDialog({ kind: 'valuation', record })}
        onDelete={(record) => remove('valuations', record.id)}
      />
      <FinancingsSection
        financings={data.financings}
        onAdd={() => setDialog({ kind: 'financing' })}
        onEdit={(record) => setDialog({ kind: 'financing', record })}
        onDelete={(record) => remove('financings', record.id)}
        onAddBalance={(financing) => setDialog({ kind: 'balance', financingId: financing.id })}
        onEditBalance={(financing, record) =>
          setDialog({ kind: 'balance', financingId: financing.id, record })
        }
        onDeleteBalance={(record) => remove('balances', record.id)}
      />
      <ExpensesSection
        expenses={data.expenses}
        onAdd={() => setDialog({ kind: 'expense' })}
        onEdit={(record) => setDialog({ kind: 'expense', record })}
        onDelete={(record) => remove('expenses', record.id)}
      />
      <PaymentsSection property={data} onDelete={(payment) => remove('payments', payment.id)} />
      <RecordDialogs dialog={dialog} propertyId={id} onClose={() => setDialog(null)} />
    </>
  )
}
