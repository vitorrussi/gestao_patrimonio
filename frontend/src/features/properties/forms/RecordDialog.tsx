// Moldura comum dos formulários da ficha: diálogo com título, campos e botões.

import type { BaseSyntheticEvent, ReactNode } from 'react'
import { FormErrorBanner } from '@/components/form'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface RecordDialogProps {
  title: string
  description?: string
  onClose: () => void
  onSubmit: (event?: BaseSyntheticEvent) => Promise<void>
  isPending: boolean
  errorMessage: string | null
  children: ReactNode
}

export function RecordDialog({
  title,
  description,
  onClose,
  onSubmit,
  isPending,
  errorMessage,
  children,
}: RecordDialogProps) {
  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-h-[90svh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>
        <form onSubmit={(event) => void onSubmit(event)} className="grid gap-4" noValidate>
          <FormErrorBanner message={errorMessage} />
          <div className="grid gap-4 sm:grid-cols-2">{children}</div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>
              Salvar
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

/** Texto padrão para quando os campos da regra estão travados por pagamentos (ESCOPO 3.5). */
export const LOCKED_RULE_HINT =
  'Travado: já há pagamentos. Para mudar, encerre esta regra e cadastre uma nova.'
