import { describe, expect, it } from 'vitest'
import {
  addMonths,
  dayOfMonth,
  formatDate,
  formatDateOrDash,
  formatMonth,
  isIsoDate,
} from './dates'

describe('formatDate', () => {
  it('converte ISO para dd/mm/aaaa sem depender do fuso', () => {
    expect(formatDate('2026-09-23')).toBe('23/09/2026')
    expect(formatDate('2026-01-01')).toBe('01/01/2026')
  })

  it('aceita 29/02 em ano bissexto', () => {
    expect(formatDate('2028-02-29')).toBe('29/02/2028')
  })

  it('recusa texto que não é ISO', () => {
    expect(() => formatDate('23/09/2026')).toThrow(RangeError)
  })

  it('mostra traço sem data', () => {
    expect(formatDateOrDash(null)).toBe('—')
    expect(formatDateOrDash('2026-09-23')).toBe('23/09/2026')
  })
})

describe('isIsoDate', () => {
  it.each([
    ['2028-02-29', true],
    ['2027-02-29', false],
    ['2026-04-31', false],
    ['2026-13-01', false],
    ['2026-00-10', false],
    ['2026-9-1', false],
    ['2026-12-31', true],
  ])('%s -> %s', (text, valid) => {
    expect(isIsoDate(text)).toBe(valid)
  })
})

describe('meses', () => {
  it('nomeia o mês em português', () => {
    expect(formatMonth({ year: 2026, month: 9 })).toBe('setembro de 2026')
    expect(formatMonth({ year: 2026, month: 3 })).toBe('março de 2026')
  })

  it('avança e volta virando o ano', () => {
    expect(addMonths({ year: 2026, month: 12 }, 1)).toEqual({ year: 2027, month: 1 })
    expect(addMonths({ year: 2026, month: 1 }, -1)).toEqual({ year: 2025, month: 12 })
    expect(addMonths({ year: 2026, month: 6 }, 0)).toEqual({ year: 2026, month: 6 })
    expect(addMonths({ year: 2026, month: 6 }, -18)).toEqual({ year: 2024, month: 12 })
  })

  it('lê o dia de uma data ISO', () => {
    expect(dayOfMonth('2026-04-30')).toBe(30)
  })
})
