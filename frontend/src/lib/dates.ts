// Datas trafegam como texto ISO ("2026-09-23"). Nada de Date aqui: evita erro de fuso
// (new Date("2026-09-23") é meia-noite UTC, que no Brasil ainda é o dia anterior).

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/

const MONTH_NAMES = [
  'janeiro',
  'fevereiro',
  'março',
  'abril',
  'maio',
  'junho',
  'julho',
  'agosto',
  'setembro',
  'outubro',
  'novembro',
  'dezembro',
]

export interface YearMonth {
  year: number
  month: number // 1 a 12
}

/** "2026-09-23" -> "23/09/2026". */
export function formatDate(iso: string): string {
  const match = ISO_DATE.exec(iso)
  if (!match) throw new RangeError(`data ISO inválida: ${iso}`)
  return `${match[3]}/${match[2]}/${match[1]}`
}

export function formatDateOrDash(iso: string | null | undefined): string {
  return iso ? formatDate(iso) : '—'
}

/** (2026, 9) -> "setembro de 2026". */
export function formatMonth({ year, month }: YearMonth): string {
  return `${MONTH_NAMES[month - 1]} de ${year}`
}

export function addMonths({ year, month }: YearMonth, delta: number): YearMonth {
  const index = year * 12 + (month - 1) + delta
  return { year: Math.floor(index / 12), month: (index % 12) + 1 }
}

/** Dia do mês de uma data ISO ("2026-09-23" -> 23). */
export function dayOfMonth(iso: string): number {
  const match = ISO_DATE.exec(iso)
  if (!match) throw new RangeError(`data ISO inválida: ${iso}`)
  return Number(match[3])
}

export function isIsoDate(text: string): boolean {
  const match = ISO_DATE.exec(text)
  if (!match) return false
  const [year, month, day] = [Number(match[1]), Number(match[2]), Number(match[3])]
  const daysInMonth = new Date(Date.UTC(year, month, 0)).getUTCDate()
  return month >= 1 && month <= 12 && day >= 1 && day <= daysInMonth
}
