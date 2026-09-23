// Envio comum dos formulários de registro: salva (cria ou edita), avisa, fecha o diálogo
// e, se a API recusar, marca a mensagem no campo certo.

import type { UseMutationResult } from '@tanstack/react-query'
import type { FieldValues, UseFormReturn } from 'react-hook-form'
import { toast } from 'sonner'
import { applyServerErrors } from '@/lib/formFields'

export interface SaveInput<TFields> {
  id?: number
  fields: TFields
}

interface SubmitOptions<TValues, TFields, TResult> {
  id?: number
  toFields: (values: TValues) => TFields
  successMessage: string
  onClose: () => void
  /** Roda antes do toast/fechamento, com o registro salvo e os valores digitados. */
  onSaved?: (result: TResult, values: TValues) => void
}

export function useSubmitRecord<TValues extends FieldValues, TFields, TResult>(
  form: UseFormReturn<TValues>,
  mutation: UseMutationResult<TResult, Error, SaveInput<TFields>>,
  { id, toFields, successMessage, onClose, onSaved }: SubmitOptions<TValues, TFields, TResult>,
) {
  return form.handleSubmit((values) =>
    mutation.mutate(
      { id, fields: toFields(values) },
      {
        onSuccess: (result) => {
          onSaved?.(result, values)
          toast.success(successMessage)
          onClose()
        },
        onError: (error) => applyServerErrors(form.setError, error),
      },
    ),
  )
}
