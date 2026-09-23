// Lista de imóveis: apelido, tipo, uso, valor de mercado, saldo devedor e líquido.
// Tabela no computador; cartões empilhados no celular.

import { Plus } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router'
import { useProperties } from '@/api/queries'
import type { PropertySummary } from '@/api/types'
import { EmptyState, LoadingState, Money, PageHeader, QueryErrorState } from '@/components/display'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { PROPERTY_TYPE_LABELS, PROPERTY_USAGE_LABELS } from '@/lib/labels'

type Filter = 'active' | 'inactive' | 'all'

const FILTERS: { value: Filter; label: string }[] = [
  { value: 'active', label: 'Ativos' },
  { value: 'inactive', label: 'Vendidos / inativos' },
  { value: 'all', label: 'Todos' },
]

function applyFilter(properties: PropertySummary[], filter: Filter): PropertySummary[] {
  if (filter === 'all') return properties
  return properties.filter((p) => p.is_active === (filter === 'active'))
}

function NameCell({ property }: { property: PropertySummary }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Link to={`/imoveis/${property.id}`} className="font-medium text-primary hover:underline">
        {property.nickname}
      </Link>
      {!property.is_active && <Badge variant="outline">Inativo</Badge>}
    </div>
  )
}

function NetValue({ property }: { property: PropertySummary }) {
  if (property.net_cents === null) {
    return <span className="text-muted-foreground">Sem valor</span>
  }
  return <Money cents={property.net_cents} />
}

function PropertyTable({ properties }: { properties: PropertySummary[] }) {
  return (
    <div className="hidden md:block">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Imóvel</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Uso</TableHead>
            <TableHead className="text-right">Valor de mercado</TableHead>
            <TableHead className="text-right">Saldo devedor</TableHead>
            <TableHead className="text-right">Patrimônio líquido</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {properties.map((property) => (
            <TableRow key={property.id}>
              <TableCell>
                <NameCell property={property} />
              </TableCell>
              <TableCell>{PROPERTY_TYPE_LABELS[property.property_type]}</TableCell>
              <TableCell>{PROPERTY_USAGE_LABELS[property.usage]}</TableCell>
              <TableCell className="text-right">
                <Money cents={property.market_value_cents} />
              </TableCell>
              <TableCell className="text-right">
                <Money cents={property.debt_cents} />
              </TableCell>
              <TableCell className="text-right">
                <NetValue property={property} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

function PropertyCards({ properties }: { properties: PropertySummary[] }) {
  return (
    <ul className="grid gap-3 md:hidden">
      {properties.map((property) => (
        <li key={property.id} className="grid gap-2 rounded-lg border p-4">
          <NameCell property={property} />
          <p className="text-sm text-muted-foreground">
            {PROPERTY_TYPE_LABELS[property.property_type]} · {PROPERTY_USAGE_LABELS[property.usage]}
          </p>
          <dl className="grid grid-cols-2 gap-1 text-sm">
            <dt className="text-muted-foreground">Valor de mercado</dt>
            <dd className="text-right">
              <Money cents={property.market_value_cents} />
            </dd>
            <dt className="text-muted-foreground">Saldo devedor</dt>
            <dd className="text-right">
              <Money cents={property.debt_cents} />
            </dd>
            <dt className="text-muted-foreground">Líquido</dt>
            <dd className="text-right font-medium">
              <NetValue property={property} />
            </dd>
          </dl>
        </li>
      ))}
    </ul>
  )
}

export function PropertyListPage() {
  const [filter, setFilter] = useState<Filter>('active')
  const properties = useProperties()

  const newButton = (
    <Button asChild>
      <Link to="/imoveis/novo">
        <Plus className="size-4" />
        Novo imóvel
      </Link>
    </Button>
  )

  if (properties.isPending) return <LoadingState />
  if (properties.isError) {
    return <QueryErrorState error={properties.error} onRetry={() => void properties.refetch()} />
  }
  const visible = applyFilter(properties.data, filter)

  return (
    <>
      <PageHeader title="Imóveis" actions={newButton} />
      <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar imóveis">
        {FILTERS.map((option) => (
          <Button
            key={option.value}
            size="sm"
            variant={filter === option.value ? 'secondary' : 'ghost'}
            aria-pressed={filter === option.value}
            onClick={() => setFilter(option.value)}
          >
            {option.label}
          </Button>
        ))}
      </div>
      {visible.length === 0 ? (
        <EmptyState message="Nenhum imóvel neste filtro." />
      ) : (
        <>
          <PropertyTable properties={visible} />
          <PropertyCards properties={visible} />
        </>
      )}
    </>
  )
}
