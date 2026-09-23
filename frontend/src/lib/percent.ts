// Percentuais e taxas trafegam como texto decimal ("33.3333"), nunca como número com casas.

function trimZeros(integer: string, decimals: string): string {
  let end = decimals.length
  while (end > 0 && decimals[end - 1] === '0') end -= 1
  const cleanDecimals = decimals.slice(0, end)
  return cleanDecimals ? `${integer},${cleanDecimals}` : integer
}

/** "33.3333" -> "33,3333"; "50.0000" -> "50". */
export function apiPercentToInput(value: string): string {
  const [integer, decimals = ''] = value.split('.')
  return trimZeros(integer, decimals)
}

/** "33,3333" -> "33,3333%"; "50.0000" -> "50%". */
export function formatPercent(value: string): string {
  return `${apiPercentToInput(value)}%`
}

const DIGITS = /^\d+$/

/** Separa "33,33" em ["33", "33"]; aceita vírgula ou ponto como decimal (não há milhar). */
function splitDecimal(text: string): [string, string] | null {
  const parts = text.replace(',', '.').split('.')
  if (parts.length > 2) return null
  const [integer, decimals = ''] = parts
  if (!DIGITS.test(integer) || (parts.length === 2 && !DIGITS.test(decimals))) return null
  if (integer.length > 4 || decimals.length > 4) return null
  return [integer, decimals]
}

/** Texto digitado ("9,5" ou "9.5") -> texto da API ("9.5"), ou null se inválido/acima do máximo. */
export function parsePercentInput(text: string, max: number): string | null {
  const parts = splitDecimal(text.trim().replace(/%$/, '').trim())
  if (!parts) return null
  const integer = parts[0].replace(/^0+(?=\d)/, '')
  const decimals = parts[1]
  const exceedsMax = Number(integer) > max || (Number(integer) === max && /[1-9]/.test(decimals))
  if (exceedsMax) return null
  return decimals ? `${integer}.${decimals}` : integer
}
