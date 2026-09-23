// Dinheiro no front: sempre centavos inteiros (regra 1). Formatação e leitura trabalham
// só com texto e inteiros — nenhum caminho passa por número com casas decimais.

const NBSP = '\u00a0'
const MAX_CENTS = 10 ** 13 // mesmo limite da API

function groupThousands(digits: string): string {
  const groups: string[] = []
  for (let end = digits.length; end > 0; end -= 3) {
    groups.unshift(digits.slice(Math.max(0, end - 3), end))
  }
  return groups.join('.')
}

/** 123456 -> "1.234,56" (sem símbolo, para campos de formulário). */
export function centsToInput(cents: number): string {
  if (!Number.isSafeInteger(cents)) {
    throw new TypeError(`centavos devem ser inteiros: ${cents}`)
  }
  const digits = String(Math.abs(cents)).padStart(3, '0')
  const reais = groupThousands(digits.slice(0, -2))
  return `${cents < 0 ? '-' : ''}${reais},${digits.slice(-2)}`
}

/** 123456 -> "R$ 1.234,56" (espaço não separável, como o Intl do navegador). */
export function formatCents(cents: number): string {
  const text = centsToInput(cents)
  return text.startsWith('-') ? `-R$${NBSP}${text.slice(1)}` : `R$${NBSP}${text}`
}

export function formatCentsOrDash(cents: number | null | undefined): string {
  return cents === null || cents === undefined ? '—' : formatCents(cents)
}

const MONEY_PATTERN = /^(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{1,2}))?$/

/**
 * Texto digitado -> centavos. Aceita "1234,56", "1.234,56", "R$ 1.234,56", "0,1".
 * Ponto é separador de milhar (grupos de 3); vírgula é decimal (até 2 casas).
 * Devolve null para texto inválido, negativo ou acima do limite.
 */
export function parseMoneyToCents(text: string): number | null {
  const clean = text.replace(/R\$/g, '').replace(/\s/g, '') // \s já inclui o espaço não separável
  const match = MONEY_PATTERN.exec(clean)
  if (!match) return null
  const reais = match[1].replace(/\./g, '')
  const decimals = (match[2] ?? '').padEnd(2, '0')
  const digits = `${reais}${decimals}`.replace(/^0+(?=\d)/, '')
  if (digits.length > 14) return null
  const cents = Number(digits)
  return cents <= MAX_CENTS ? cents : null
}
