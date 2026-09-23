import { zodResolver } from '@hookform/resolvers/zod'
import { type UseFormReturn, useForm } from 'react-hook-form'
import { useSaveExpense } from '@/api/queries'
import type { Expense } from '@/api/types'
import { CheckboxRow, FormInput, FormSelect } from '@/components/form'
import { expenseHelp } from '@/features/help/content'
import { errorMessage } from '@/lib/apiErrors'
import { MONEY_INPUT_PROPS } from '@/lib/formFields'
import { EXPENSE_TYPE_LABELS, FREQUENCY_LABELS, optionsOf } from '@/lib/labels'
import { LOCKED_RULE_HINT, RecordDialog } from './RecordDialog'
import {
  type ExpenseFormValues,
  expenseSchema,
  expenseToForm,
  formToExpense,
} from './recordSchemas'
import { useSubmitRecord } from './useSubmitRecord'

type Form = UseFormReturn<ExpenseFormValues>

function DescriptionFields({ form }: { form: Form }) {
  return (
    <>
      <FormSelect
        form={form}
        name="expense_type"
        label="Tipo"
        help={expenseHelp.expense_type}
        options={optionsOf(EXPENSE_TYPE_LABELS)}
      />
      <FormInput
        form={form}
        name="description"
        label="Descrição"
        help={expenseHelp.description}
        inputProps={{ placeholder: 'Ex.: IPTU 2026 — 10x' }}
      />
      <FormInput
        form={form}
        name="amount"
        label="Valor de cada vencimento (R$)"
        help={expenseHelp.amount}
        inputProps={MONEY_INPUT_PROPS}
      />
    </>
  )
}

/** Campos que definem quando os vencimentos caem: travados depois do 1º pagamento. */
function RuleFields({ form, locked }: { form: Form; locked: boolean }) {
  const lockedHint = locked ? LOCKED_RULE_HINT : undefined
  return (
    <>
      <FormSelect
        form={form}
        name="frequency"
        label="Periodicidade"
        help={expenseHelp.frequency}
        options={optionsOf(FREQUENCY_LABELS)}
        hint={lockedHint}
        disabled={locked}
      />
      <FormInput
        form={form}
        name="due_day"
        label="Dia de vencimento"
        hint={lockedHint ?? 'Em meses mais curtos, vence no último dia.'}
        help={expenseHelp.due_day}
        inputProps={{ inputMode: 'numeric', readOnly: locked }}
      />
      <FormInput
        form={form}
        name="start_date"
        label="Início"
        hint={lockedHint}
        help={expenseHelp.start_date}
        inputProps={{ type: 'date', readOnly: locked }}
      />
      <FormInput
        form={form}
        name="installment_count"
        label="Nº de parcelas (opcional)"
        hint={lockedHint ?? 'Ex.: 10 para IPTU parcelado.'}
        help={expenseHelp.installment_count}
        inputProps={{ inputMode: 'numeric', readOnly: locked }}
      />
    </>
  )
}

function EndFields({ form }: { form: Form }) {
  return (
    <>
      <FormInput
        form={form}
        name="end_date"
        label="Data de fim (opcional)"
        hint="Use para encerrar a despesa mantendo o histórico."
        help={expenseHelp.end_date}
        inputProps={{ type: 'date' }}
      />
      <div className="flex items-center sm:pt-6">
        <CheckboxRow
          id="is_active"
          label="Ativa"
          help={expenseHelp.is_active}
          {...form.register('is_active')}
        />
      </div>
    </>
  )
}

interface ExpenseDialogProps {
  propertyId: number
  expense?: Expense
  onClose: () => void
}

export function ExpenseDialog({ propertyId, expense, onClose }: ExpenseDialogProps) {
  const save = useSaveExpense(propertyId)
  const form = useForm<ExpenseFormValues>({
    resolver: zodResolver(expenseSchema),
    defaultValues: expenseToForm(expense),
  })
  const onSubmit = useSubmitRecord(form, save, {
    id: expense?.id,
    toFields: formToExpense,
    successMessage: 'Despesa salva.',
    onClose,
  })

  return (
    <RecordDialog
      title={expense ? 'Editar despesa' : 'Nova despesa recorrente'}
      description="Os vencimentos são calculados a partir destas regras."
      onClose={onClose}
      onSubmit={onSubmit}
      isPending={save.isPending}
      errorMessage={save.isError ? errorMessage(save.error) : null}
    >
      <DescriptionFields form={form} />
      <RuleFields form={form} locked={expense?.has_payments ?? false} />
      <EndFields form={form} />
    </RecordDialog>
  )
}
