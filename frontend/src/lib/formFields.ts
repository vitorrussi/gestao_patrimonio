// Validadores Zod dos campos de formulário. O formulário guarda o TEXTO digitado;
// a conversão para o formato da API (centavos, "33.3333", null) acontece só no envio.

import type { FieldValues, Path, UseFormSetError } from 'react-hook-form'
import { z } from 'zod'
import { fieldErrors } from '@/lib/apiErrors'
import { isIsoDate } from '@/lib/dates'
import { parseMoneyToCents } from '@/lib/money'
import { parsePercentInput } from '@/lib/percent'

const MONEY_MESSAGE = 'Valor inválido. Ex.: 1.234,56'

/** Props dos campos de dinheiro: teclado numérico no celular e exemplo do formato. */
export const MONEY_INPUT_PROPS = { inputMode: 'decimal', placeholder: '0,00' } as const

export const requiredText = (max: number) =>
  z.string().trim().min(1, 'Campo obrigatório.').max(max, `Máximo de ${max} caracteres.`)

export const optionalText = (max: number) =>
  z.string().trim().max(max, `Máximo de ${max} caracteres.`)

export const requiredMoney = z
  .string()
  .refine((value) => parseMoneyToCents(value) !== null, MONEY_MESSAGE)

export const optionalMoney = z
  .string()
  .refine((value) => value.trim() === '' || parseMoneyToCents(value) !== null, MONEY_MESSAGE)

export const percentText = (max: number) =>
  z
    .string()
    .refine(
      (value) => parsePercentInput(value, max) !== null,
      `Informe um número de 0 a ${max}, com até 4 casas. Ex.: 33,3333`,
    )

export const requiredDate = z.string().refine(isIsoDate, 'Informe a data.')

export const optionalDate = z
  .string()
  .refine((value) => value === '' || isIsoDate(value), 'Data inválida.')

export const integerText = (min: number, max: number, optional = false) =>
  z.string().refine((value) => {
    if (optional && value.trim() === '') return true
    if (!/^\d+$/.test(value.trim())) return false
    const number = Number(value)
    return number >= min && number <= max
  }, `Informe um número inteiro de ${min} a ${max}.`)

// --- conversões no envio (os valores já passaram pela validação acima) ---

export function toCents(text: string): number {
  const cents = parseMoneyToCents(text)
  if (cents === null) throw new Error(`valor não validado: ${text}`)
  return cents
}

export function toOptionalCents(text: string): number {
  return text.trim() === '' ? 0 : toCents(text)
}

export function toPercent(text: string, max: number): string {
  const value = parsePercentInput(text, max)
  if (value === null) throw new Error(`percentual não validado: ${text}`)
  return value
}

export function emptyToNull(text: string): string | null {
  return text.trim() === '' ? null : text.trim()
}

export function toOptionalInt(text: string): number | null {
  return text.trim() === '' ? null : Number(text)
}

/** Marca nos campos do formulário os erros de validação devolvidos pela API. */
export function applyServerErrors<T extends FieldValues>(
  setError: UseFormSetError<T>,
  error: unknown,
): boolean {
  const errors = fieldErrors(error)
  for (const [apiField, message] of Object.entries(errors)) {
    setError(apiField.replace(/_cents$/, '') as Path<T>, { message })
  }
  return Object.keys(errors).length > 0
}

export const enumText = (labels: Record<string, string>) =>
  z.string().refine((value) => Object.hasOwn(labels, value), 'Escolha uma opção.')

export const optionalEnumText = (labels: Record<string, string>) =>
  z.string().refine((value) => value === '' || Object.hasOwn(labels, value), 'Escolha uma opção.')

/** Mesmo critério da API: algo@domínio.tld, sem espaços. */
export function looksLikeEmail(text: string): boolean {
  const parts = text.split('@')
  if (parts.length !== 2 || /\s/.test(text)) return false
  const [local, domain] = parts
  const dot = domain.lastIndexOf('.')
  return local.length > 0 && dot > 0 && dot < domain.length - 1
}
