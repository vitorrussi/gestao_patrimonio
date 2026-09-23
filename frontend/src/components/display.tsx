// Peças de exibição reaproveitadas pelas telas.

import { AlertCircle, Inbox } from 'lucide-react'
import type { ReactNode } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { errorMessage } from '@/lib/apiErrors'
import { DUE_STATUS_LABELS, type DueStatus } from '@/lib/labels'
import { formatCentsOrDash } from '@/lib/money'
import { cn } from '@/lib/utils'

export function Money({ cents, className }: { cents: number | null; className?: string }) {
  const negative = cents !== null && cents < 0
  return (
    <span className={cn('tabular-nums', negative && 'text-destructive', className)}>
      {formatCentsOrDash(cents)}
    </span>
  )
}

const STATUS_VARIANT = {
  pago: 'secondary',
  a_pagar: 'outline',
  atrasado: 'destructive',
} as const

export function StatusBadge({ status }: { status: DueStatus }) {
  return <Badge variant={STATUS_VARIANT[status]}>{DUE_STATUS_LABELS[status]}</Badge>
}

interface PageHeaderProps {
  title: string
  description?: ReactNode
  actions?: ReactNode
}

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div className="grid gap-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">{title}</h1>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  )
}

export function LoadingState() {
  return (
    <div className="grid gap-3" aria-busy="true" aria-label="Carregando">
      <Skeleton className="h-8 w-1/3" />
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-24 w-full" />
    </div>
  )
}

export function QueryErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-start gap-3 rounded-lg border p-4">
      <p className="flex items-center gap-2 text-sm text-destructive">
        <AlertCircle className="size-4" />
        {errorMessage(error)}
      </p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Tentar de novo
        </Button>
      )}
    </div>
  )
}

export function EmptyState({ message, action }: { message: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed p-8 text-center">
      <Inbox className="size-6 text-muted-foreground" />
      <p className="text-sm text-muted-foreground">{message}</p>
      {action}
    </div>
  )
}
