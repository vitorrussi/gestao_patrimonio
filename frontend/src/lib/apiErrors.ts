// Erros da API -> mensagens em português. A API manda `type` estável; o `message`
// em inglês do Pydantic nunca aparece na tela. Mensagens que a própria API escreveu
// em português (value_error, trava de regra) são aproveitadas.

import { ApiError } from '@/api/client'
import type { ErrorDetail } from '@/api/types'

const ERROR_CODE_MESSAGES: Record<string, string> = {
  invalid_credentials: 'E-mail ou senha inválidos.',
  email_already_registered: 'Este e-mail já está cadastrado.',
  registration_disabled: 'O cadastro de novas contas está desativado.',
  payment_already_registered: 'Este vencimento já tem pagamento registrado.',
  not_found: 'Registro não encontrado. Ele pode ter sido excluído.',
  unauthorized: 'Sua sessão expirou. Entre novamente.',
}

const DETAIL_TYPE_MESSAGES: Record<string, string> = {
  missing: 'Campo obrigatório.',
  string_too_short: 'Campo obrigatório.',
  string_too_long: 'Texto longo demais.',
  greater_than_equal: 'Valor abaixo do mínimo.',
  less_than_equal: 'Valor acima do máximo.',
  decimal_max_places: 'Casas decimais demais.',
  decimal_max_digits: 'Número grande demais.',
  enum: 'Escolha uma das opções.',
  extra_forbidden: 'Campo não permitido.',
  not_a_due_date: 'Esta data não é um vencimento desta despesa ou financiamento.',
  json_required: 'Não foi possível enviar os dados.',
  json_object_required: 'Não foi possível enviar os dados.',
}

const VALUE_ERROR_PREFIX = 'Value error, '

export function detailMessage(detail: ErrorDetail): string {
  if (detail.type === 'value_error' && detail.message.startsWith(VALUE_ERROR_PREFIX)) {
    return capitalize(detail.message.slice(VALUE_ERROR_PREFIX.length))
  }
  return DETAIL_TYPE_MESSAGES[detail.type] ?? 'Valor inválido.'
}

function capitalize(text: string): string {
  const sentence = text.charAt(0).toUpperCase() + text.slice(1)
  return sentence.endsWith('.') ? sentence : `${sentence}.`
}

/** Mensagem geral para mostrar num aviso. */
export function errorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return 'Não foi possível falar com o servidor. Verifique a conexão e tente de novo.'
  }
  if (error.code === 'rule_locked_by_payments' && error.body?.message) {
    return error.body.message
  }
  if (error.code === 'validation_error') {
    const general = error.details.find((d) => d.field === null)
    return general ? detailMessage(general) : 'Confira os campos destacados.'
  }
  return ERROR_CODE_MESSAGES[error.code] ?? 'Algo deu errado. Tente de novo.'
}

/** Erros por campo (para marcar cada campo do formulário). */
export function fieldErrors(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError) || error.code !== 'validation_error') return {}
  const errors: Record<string, string> = {}
  for (const detail of error.details) {
    if (detail.field && !(detail.field in errors)) {
      errors[detail.field] = detailMessage(detail)
    }
  }
  return errors
}
