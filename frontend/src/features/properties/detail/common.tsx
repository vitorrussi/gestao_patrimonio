// Peças comuns das seções da ficha: cabeçalho com botão "adicionar" e ações de linha.

import { Pencil, Plus, Trash2 } from 'lucide-react'
import type { ReactNode } from 'react'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { Button } from '@/components/ui/button'
import { Card, CardAction, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface SectionProps {
  title: string
  addLabel?: string
  onAdd?: () => void
  children: ReactNode
}

export function Section({ title, addLabel, onAdd, children }: SectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {onAdd && (
          <CardAction>
            <Button size="sm" variant="outline" onClick={onAdd}>
              <Plus className="size-4" />
              {addLabel}
            </Button>
          </CardAction>
        )}
      </CardHeader>
      <CardContent className="grid gap-3">{children}</CardContent>
    </Card>
  )
}

interface RowActionsProps {
  itemLabel: string
  deleteWarning: string
  onEdit?: () => void
  onDelete: () => void
}

export function RowActions({ itemLabel, deleteWarning, onEdit, onDelete }: RowActionsProps) {
  return (
    <div className="flex shrink-0 gap-1">
      {onEdit && (
        <Button size="icon-sm" variant="ghost" onClick={onEdit} aria-label={`Editar ${itemLabel}`}>
          <Pencil className="size-4" />
        </Button>
      )}
      <ConfirmDialog
        title={`Excluir ${itemLabel}?`}
        description={deleteWarning}
        onConfirm={onDelete}
        trigger={
          <Button size="icon-sm" variant="ghost" aria-label={`Excluir ${itemLabel}`}>
            <Trash2 className="size-4" />
          </Button>
        }
      />
    </div>
  )
}

export function EmptyLine({ children }: { children: ReactNode }) {
  return <p className="text-sm text-muted-foreground">{children}</p>
}
