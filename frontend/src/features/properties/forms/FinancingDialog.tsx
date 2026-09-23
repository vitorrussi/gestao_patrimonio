import { zodResolver } from '@hookform/resolvers/zod'
import { type UseFormReturn, useForm } from 'react-hook-form'
import { useSaveFinancing } from '@/api/queries'
import type { Financing } from '@/api/types'
import { CheckboxRow, FormInput, FormSelect } from '@/components/form'
import { errorMessage } from '@/lib/apiErrors'
import { MONEY_INPUT_PROPS } from '@/lib/formFields'
import { AMORTIZATION_SYSTEM_LABELS, INTEREST_INDEX_LABELS, optionsOf } from '@/lib/labels'
import { LOCKED_RULE_HINT, RecordDialog } from './RecordDialog'
import {
  type FinancingFormValues,
  financingSchema,
  financingToForm,
  formToFinancing,
} from './recordSchemas'
import { useSubmitRecord } from './useSubmitRecord'

type Form = UseFormReturn<FinancingFormValues>

function ContractFields({ form }: { form: Form }) {
  return (
    <>
      <FormInput
        form={form}
        name="lender"
        label="Credor"
        inputProps={{ placeholder: 'Ex.: Caixa' }}
      />
      <FormInput form={form} name="contract_number" label="Número do contrato" />
      <FormInput
        form={form}
        name="financed_amount"
        label="Valor financiado (R$)"
        inputProps={MONEY_INPUT_PROPS}
      />
      <FormInput
        form={form}
        name="current_installment"
        label="Parcela atual (R$)"
        inputProps={MONEY_INPUT_PROPS}
      />
      <FormSelect
        form={form}
        name="amortization_system"
        label="Sistema de amortização"
        options={optionsOf(AMORTIZATION_SYSTEM_LABELS)}
      />
      <FormSelect
        form={form}
        name="interest_index"
        label="Indexador"
        options={optionsOf(INTEREST_INDEX_LABELS)}
      />
      <FormInput
        form={form}
        name="annual_interest_rate"
        label="Juros ao ano (%)"
        inputProps={{ inputMode: 'decimal', placeholder: 'Ex.: 9,5' }}
      />
    </>
  )
}

/** Campos que definem as datas das parcelas: travados depois do 1º pagamento. */
function ScheduleFields({ form, locked }: { form: Form; locked: boolean }) {
  const lockedHint = locked ? LOCKED_RULE_HINT : undefined
  return (
    <>
      <FormInput
        form={form}
        name="term_months"
        label="Prazo total (meses)"
        inputProps={{ inputMode: 'numeric' }}
      />
      <FormInput
        form={form}
        name="first_installment_date"
        label="Data da 1ª parcela"
        hint={lockedHint}
        inputProps={{ type: 'date', readOnly: locked }}
      />
      <FormInput
        form={form}
        name="due_day"
        label="Dia de vencimento"
        hint={lockedHint ?? 'A 1ª parcela precisa cair neste dia.'}
        inputProps={{ inputMode: 'numeric', readOnly: locked }}
      />
      <div className="sm:col-span-2">
        <CheckboxRow
          id="is_paid_off"
          label="Quitado (sai da dívida e dos compromissos)"
          {...form.register('is_paid_off')}
        />
      </div>
    </>
  )
}

interface FinancingDialogProps {
  propertyId: number
  financing?: Financing
  onClose: () => void
}

export function FinancingDialog({ propertyId, financing, onClose }: FinancingDialogProps) {
  const save = useSaveFinancing(propertyId)
  const form = useForm<FinancingFormValues>({
    resolver: zodResolver(financingSchema),
    defaultValues: financingToForm(financing),
  })
  const onSubmit = useSubmitRecord(form, save, {
    id: financing?.id,
    toFields: formToFinancing,
    successMessage: 'Financiamento salvo.',
    onClose,
  })

  return (
    <RecordDialog
      title={financing ? 'Editar financiamento' : 'Novo financiamento'}
      description="A parcela atual é lançada à mão e aparece nos compromissos de cada mês."
      onClose={onClose}
      onSubmit={onSubmit}
      isPending={save.isPending}
      errorMessage={save.isError ? errorMessage(save.error) : null}
    >
      <ContractFields form={form} />
      <ScheduleFields form={form} locked={financing?.has_payments ?? false} />
    </RecordDialog>
  )
}
