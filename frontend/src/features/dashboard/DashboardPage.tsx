// Painel geral: patrimônio bruto, dívida, líquido e imóveis por tipo (só imóveis ativos).

import { Link } from 'react-router'
import type { Dashboard } from '@/api/types'
import { useDashboard } from '@/api/queries'
import { EmptyState, LoadingState, Money, PageHeader, QueryErrorState } from '@/components/display'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PROPERTY_TYPE_LABELS, type PropertyType } from '@/lib/labels'

function TotalCard({ title, cents, hint }: { title: string; cents: number; hint?: string }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-2xl">
          <Money cents={cents} />
        </CardTitle>
      </CardHeader>
      {hint && <CardContent className="text-xs text-muted-foreground">{hint}</CardContent>}
    </Card>
  )
}

function Warnings({ data }: { data: Dashboard }) {
  const warnings = []
  if (data.properties_without_value > 0) {
    const n = data.properties_without_value
    warnings.push(
      `${n} ${n === 1 ? 'imóvel está' : 'imóveis estão'} sem avaliação de mercado e ${n === 1 ? 'fica' : 'ficam'} fora do patrimônio bruto.`,
    )
  }
  if (data.debt_estimated) {
    warnings.push(
      'Há financiamento sem saldo devedor lançado; a dívida usa o valor financiado como estimativa.',
    )
  }
  if (warnings.length === 0) return null
  return (
    <ul className="grid gap-1 rounded-lg border bg-muted/40 p-3 text-sm text-muted-foreground">
      {warnings.map((warning) => (
        <li key={warning}>{warning}</li>
      ))}
    </ul>
  )
}

function CountByType({ counts }: { counts: Dashboard['count_by_type'] }) {
  const entries = Object.entries(counts) as [PropertyType, number][]
  return (
    <Card>
      <CardHeader>
        <CardTitle>Imóveis por tipo</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="grid gap-2 sm:grid-cols-2">
          {entries.map(([type, count]) => (
            <li key={type} className="flex justify-between border-b pb-2 text-sm">
              <span>{PROPERTY_TYPE_LABELS[type]}</span>
              <span className="font-medium tabular-nums">{count}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const dashboard = useDashboard()

  if (dashboard.isPending) return <LoadingState />
  if (dashboard.isError) {
    return <QueryErrorState error={dashboard.error} onRetry={() => void dashboard.refetch()} />
  }
  const data = dashboard.data

  return (
    <>
      <PageHeader
        title="Painel"
        description="Totais dos imóveis ativos, com a sua participação em cada um."
        actions={
          <Button variant="outline" asChild>
            <Link to="/compromissos">Compromissos do mês</Link>
          </Button>
        }
      />
      {data.property_count === 0 ? (
        <EmptyState
          message="Nenhum imóvel ativo cadastrado ainda."
          action={
            <Button asChild>
              <Link to="/imoveis/novo">Cadastrar imóvel</Link>
            </Button>
          }
        />
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <TotalCard title="Patrimônio bruto" cents={data.gross_total_cents} />
            <TotalCard title="Dívida total" cents={data.debt_total_cents} />
            <TotalCard
              title="Patrimônio líquido"
              cents={data.net_total_cents}
              hint={`${data.property_count} ${data.property_count === 1 ? 'imóvel ativo' : 'imóveis ativos'}`}
            />
          </div>
          <Warnings data={data} />
          <CountByType counts={data.count_by_type} />
        </>
      )}
    </>
  )
}
