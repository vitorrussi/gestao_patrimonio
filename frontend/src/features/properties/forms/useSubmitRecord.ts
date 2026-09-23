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

interface SubmitOptions<TValues, TFields> {
  id?: number
  toFields: (values: TValues) => TFields
  successMessage: string
  onClose: () => void
}

export function useSubmitRecord<TValues extends FieldValues, TFields, TResult>(
  form: UseFormReturn<TValues>,
  mutation: UseMutationResult<TResult, Error, SaveInput<TFields>>,
  { id, toFields, successMessage, onClose }: SubmitOptions<TValues, TFields>,
) {
  return form.handleSubmit((values) =>
    mutation.mutate(
      { id, fields: toFields(values) },
      {
        onSuccess: () => {
          toast.success(successMessage)
          onClose()
        },
        onError: (error) => applyServerErrors(form.setError, error),
      },
    ),
  )
}
