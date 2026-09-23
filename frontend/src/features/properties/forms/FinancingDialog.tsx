import { zodResolver } from '@hookform/resolvers/zod'
import { type UseFormReturn, useForm, useWatch } from 'react-hook-form'
import { toast } from 'sonner'
import { useCreateBalance, useSaveFinancing } from '@/api/queries'
import type { Financing } from '@/api/types'
import { CheckboxRow, FormInput, FormSelect } from '@/components/form'
import { financingHelp } from '@/features/help/content'
import { errorMessage } from '@/lib/apiErrors'
import { MONEY_INPUT_PROPS, toCents } from '@/lib/formFields'
import { AMORTIZATION_SYSTEM_LABELS, INTEREST_INDEX_LABELS, optionsOf } from '@/lib/labels'
import { LOCKED_RULE_HINT, RecordDialog } from './RecordDialog'
import {
  FINANCING_MODE_LABELS,
  type FinancingFormValues,
  financingSchema,
  financingToForm,
  formToFinancing,
} from './recordSchemas'
import { useSubmitRecord } from './useSubmitRecord'

type Form = UseFormReturn<FinancingFormValues>

function ContractIdentityFields({ form }: { form: Form }) {
  return (
    <>
      <FormInput
        form={form}
        name="lender"
        label="Credor"
        help={financingHelp.lender}
        inputProps={{ placeholder: 'Ex.: Caixa' }}
      />
      <FormInput
        form={form}
        name="contract_number"
        label="Número do contrato"
        help={financingHelp.contract_number}
      />
      <FormInput
        form={form}
        name="financed_amount"
        label="Valor financiado (R$)"
        help={financingHelp.financed_amount}
        inputProps={MONEY_INPUT_PROPS}
      />
      <FormInput
        form={form}
        name="current_installment"
        label="Parcela atual (R$)"
        help={financingHelp.current_installment}
        inputProps={MONEY_INPUT_PROPS}
      />
    </>
  )
}

function ContractRateFields({ form }: { form: Form }) {
  return (
    <>
      <FormSelect
        form={form}
        name="amortization_system"
        label="Sistema de amortização"
        help={financingHelp.amortization_system}
        options={optionsOf(AMORTIZATION_SYSTEM_LABELS)}
      />
      <FormSelect
        form={form}
        name="interest_index"
        label="Indexador"
        help={financingHelp.interest_index}
        options={optionsOf(INTEREST_INDEX_LABELS)}
      />
      <FormInput
        form={form}
        name="annual_interest_rate"
        label="Juros ao ano (%)"
        help={financingHelp.annual_interest_rate}
        inputProps={{ inputMode: 'decimal', placeholder: 'Ex.: 9,5' }}
      />
    </>
  )
}

function ContractFields({ form }: { form: Form }) {
  return (
    <>
      <ContractIdentityFields form={form} />
      <ContractRateFields form={form} />
    </>
  )
}

/** Só aparece ao criar: escolhe se o prazo/data são do contrato ou do que falta pagar. */
function ModeField({ form }: { form: Form }) {
  return (
    <div className="sm:col-span-2">
      <FormSelect
        form={form}
        name="mode"
        label="Situação do financiamento"
        help={financingHelp.mode}
        options={optionsOf(FINANCING_MODE_LABELS)}
      />
    </div>
  )
}

/** Campos que definem as datas das parcelas: travados depois do 1º pagamento. */
function ScheduleFields({ form, locked, mode }: { form: Form; locked: boolean; mode: string }) {
  const lockedHint = locked ? LOCKED_RULE_HINT : undefined
  const existing = mode === 'existente'
  return (
    <>
      <FormInput
        form={form}
        name="term_months"
        label={existing ? 'Prazo restante (meses)' : 'Prazo total (meses)'}
        help={financingHelp.term_months}
        inputProps={{ inputMode: 'numeric' }}
      />
      <FormInput
        form={form}
        name="first_installment_date"
        label={existing ? 'Data da próxima parcela' : 'Data da 1ª parcela'}
        hint={lockedHint}
        help={financingHelp.first_installment_date}
        inputProps={{ type: 'date', readOnly: locked }}
      />
      <FormInput
        form={form}
        name="due_day"
        label="Dia de vencimento"
        hint={lockedHint ?? 'A parcela acima precisa cair neste dia.'}
        help={financingHelp.due_day}
        inputProps={{ inputMode: 'numeric', readOnly: locked }}
      />
      <div className="sm:col-span-2">
        <CheckboxRow
          id="is_paid_off"
          label="Quitado (sai da dívida e dos compromissos)"
          help={financingHelp.is_paid_off}
          {...form.register('is_paid_off')}
        />
      </div>
    </>
  )
}

/** Só aparece para financiamento existente: sem isso a dívida seria estimada pelo valor financiado total. */
function InitialDebtFields({ form }: { form: Form }) {
  return (
    <>
      <FormInput
        form={form}
        name="initial_debt_balance_date"
        label="Data do saldo devedor"
        help={financingHelp.initial_debt_balance_date}
        inputProps={{ type: 'date' }}
      />
      <FormInput
        form={form}
        name="initial_debt_balance"
        label="Saldo devedor atual (R$)"
        hint="Copie do extrato do banco."
        help={financingHelp.initial_debt_balance}
        inputProps={MONEY_INPUT_PROPS}
      />
    </>
  )
}

interface FinancingDialogProps {
  propertyId: number
  financing?: Financing
  onClose: () => void
}

export function FinancingDialog({ propertyId, financing, onClose }: FinancingDialogProps) {
  const isCreating = !financing
  const save = useSaveFinancing(propertyId)
  const createBalance = useCreateBalance()
  const form = useForm<FinancingFormValues>({
    resolver: zodResolver(financingSchema),
    defaultValues: financingToForm(financing),
  })
  const mode = useWatch({ control: form.control, name: 'mode' })
  const onSubmit = useSubmitRecord(form, save, {
    id: financing?.id,
    toFields: formToFinancing,
    successMessage: 'Financiamento salvo.',
    onClose,
    onSaved: (result, values) => {
      if (!isCreating || values.mode !== 'existente') return
      createBalance.mutate(
        {
          financingId: result.id,
          fields: {
            balance_date: values.initial_debt_balance_date,
            balance_cents: toCents(values.initial_debt_balance),
          },
        },
        {
          onError: (error) =>
            toast.error(
              `Financiamento salvo, mas o saldo devedor não pôde ser registrado: ${errorMessage(error)}. Lance-o na ficha do imóvel.`,
            ),
        },
      )
    },
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
      {isCreating && <ModeField form={form} />}
      <ContractFields form={form} />
      <ScheduleFields form={form} locked={financing?.has_payments ?? false} mode={mode} />
      {isCreating && mode === 'existente' && <InitialDebtFields form={form} />}
    </RecordDialog>
  )
}
