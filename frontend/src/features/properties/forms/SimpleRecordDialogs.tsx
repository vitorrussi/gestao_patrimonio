// Formulários curtos da ficha: avaliação de mercado e registro de saldo devedor.

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useSaveBalance, useSaveValuation } from '@/api/queries'
import type { Balance, Valuation } from '@/api/types'
import { FormInput, FormSelect } from '@/components/form'
import { balanceHelp, valuationHelp } from '@/features/help/content'
import { errorMessage } from '@/lib/apiErrors'
import { MONEY_INPUT_PROPS } from '@/lib/formFields'
import { VALUATION_SOURCE_LABELS, optionsOf } from '@/lib/labels'
import { RecordDialog } from './RecordDialog'
import {
  type BalanceFormValues,
  type ValuationFormValues,
  balanceSchema,
  balanceToForm,
  formToBalance,
  formToValuation,
  valuationSchema,
  valuationToForm,
} from './recordSchemas'
import { useSubmitRecord } from './useSubmitRecord'

interface ValuationDialogProps {
  propertyId: number
  valuation?: Valuation
  onClose: () => void
}

export function ValuationDialog({ propertyId, valuation, onClose }: ValuationDialogProps) {
  const save = useSaveValuation(propertyId)
  const form = useForm<ValuationFormValues>({
    resolver: zodResolver(valuationSchema),
    defaultValues: valuationToForm(valuation),
  })
  const onSubmit = useSubmitRecord(form, save, {
    id: valuation?.id,
    toFields: formToValuation,
    successMessage: 'Avaliação salva.',
    onClose,
  })

  return (
    <RecordDialog
      title={valuation ? 'Editar avaliação' : 'Nova avaliação de mercado'}
      description="O valor atual do imóvel é o da avaliação com a data mais recente."
      onClose={onClose}
      onSubmit={onSubmit}
      isPending={save.isPending}
      errorMessage={save.isError ? errorMessage(save.error) : null}
    >
      <FormInput
        form={form}
        name="valuation_date"
        label="Data"
        help={valuationHelp.valuation_date}
        inputProps={{ type: 'date' }}
      />
      <FormInput
        form={form}
        name="value"
        label="Valor (R$)"
        help={valuationHelp.value}
        inputProps={MONEY_INPUT_PROPS}
      />
      <FormSelect
        form={form}
        name="source"
        label="Fonte"
        help={valuationHelp.source}
        options={optionsOf(VALUATION_SOURCE_LABELS)}
      />
    </RecordDialog>
  )
}

interface BalanceDialogProps {
  financingId: number
  balance?: Balance
  onClose: () => void
}

export function BalanceDialog({ financingId, balance, onClose }: BalanceDialogProps) {
  const save = useSaveBalance(financingId)
  const form = useForm<BalanceFormValues>({
    resolver: zodResolver(balanceSchema),
    defaultValues: balanceToForm(balance),
  })
  const onSubmit = useSubmitRecord(form, save, {
    id: balance?.id,
    toFields: formToBalance,
    successMessage: 'Saldo devedor salvo.',
    onClose,
  })

  return (
    <RecordDialog
      title={balance ? 'Editar saldo devedor' : 'Lançar saldo devedor'}
      description="Copie do extrato do banco. O saldo mais recente é a dívida atual."
      onClose={onClose}
      onSubmit={onSubmit}
      isPending={save.isPending}
      errorMessage={save.isError ? errorMessage(save.error) : null}
    >
      <FormInput
        form={form}
        name="balance_date"
        label="Data do extrato"
        help={balanceHelp.balance_date}
        inputProps={{ type: 'date' }}
      />
      <FormInput
        form={form}
        name="balance"
        label="Saldo devedor (R$)"
        help={balanceHelp.balance}
        inputProps={MONEY_INPUT_PROPS}
      />
    </RecordDialog>
  )
}
