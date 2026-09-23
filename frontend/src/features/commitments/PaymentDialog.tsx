// Registrar pagamento a partir de um vencimento (já vem com a data e o valor previsto).

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'
import { useCreatePayment } from '@/api/queries'
import type { DueItem } from '@/api/types'
import { FormInput } from '@/components/form'
import { RecordDialog } from '@/features/properties/forms/RecordDialog'
import { errorMessage } from '@/lib/apiErrors'
import { formatDate } from '@/lib/dates'
import {
  MONEY_INPUT_PROPS,
  applyServerErrors,
  requiredDate,
  requiredMoney,
  toCents,
} from '@/lib/formFields'
import { centsToInput, formatCents } from '@/lib/money'

const paymentSchema = z.object({ payment_date: requiredDate, amount_paid: requiredMoney })
type PaymentFormValues = z.infer<typeof paymentSchema>

function usePaymentForm(item: DueItem, today: string, onClose: () => void) {
  const create = useCreatePayment()
  const form = useForm<PaymentFormValues>({
    resolver: zodResolver(paymentSchema),
    defaultValues: { payment_date: today, amount_paid: centsToInput(item.expected_amount_cents) },
  })
  const onSubmit = form.handleSubmit((values) =>
    create.mutate(
      {
        source_kind: item.source_kind,
        source_id: item.source_id,
        reference_due_date: item.due_date,
        payment_date: values.payment_date,
        amount_paid_cents: toCents(values.amount_paid),
      },
      {
        onSuccess: () => {
          toast.success('Pagamento registrado.')
          onClose()
        },
        onError: (error) => applyServerErrors(form.setError, error),
      },
    ),
  )
  return { create, form, onSubmit }
}

interface PaymentDialogProps {
  item: DueItem
  today: string
  onClose: () => void
}

export function PaymentDialog({ item, today, onClose }: PaymentDialogProps) {
  const { create, form, onSubmit } = usePaymentForm(item, today, onClose)

  return (
    <RecordDialog
      title="Registrar pagamento"
      description={`${item.description} — ${item.property_nickname}. Vencimento ${formatDate(item.due_date)}, previsto ${formatCents(item.expected_amount_cents)}.`}
      onClose={onClose}
      onSubmit={onSubmit}
      isPending={create.isPending}
      errorMessage={create.isError ? errorMessage(create.error) : null}
    >
      <FormInput
        form={form}
        name="payment_date"
        label="Data do pagamento"
        inputProps={{ type: 'date' }}
      />
      <FormInput
        form={form}
        name="amount_paid"
        label="Valor pago (R$)"
        hint="Pode incluir juros ou multa."
        inputProps={MONEY_INPUT_PROPS}
      />
    </RecordDialog>
  )
}
