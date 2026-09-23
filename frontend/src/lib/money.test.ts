import { describe, expect, it } from 'vitest'
import { centsToInput, formatCents, formatCentsOrDash, parseMoneyToCents } from './money'

const NBSP = '\u00a0'

describe('formatCents', () => {
  it.each([
    [0, '0,00'],
    [1, '0,01'],
    [10, '0,10'],
    [100, '1,00'],
    [123456, '1.234,56'],
    [100_000_000, '1.000.000,00'],
    [10 ** 13, '100.000.000.000,00'],
  ])('%i centavos -> R$ %s', (cents, text) => {
    expect(formatCents(cents)).toBe(`R$${NBSP}${text}`)
  })

  it('formata negativos (ex.: patrimônio líquido negativo)', () => {
    expect(formatCents(-5_000_000)).toBe(`-R$${NBSP}50.000,00`)
    expect(formatCents(-1)).toBe(`-R$${NBSP}0,01`)
  })

  it('bate com o formato do Intl do navegador', () => {
    const intl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
    expect(formatCents(123456)).toBe(intl.format(1234.56))
  })

  it('recusa valores que não são centavos inteiros', () => {
    expect(() => formatCents(1.5)).toThrow(TypeError)
    expect(() => formatCents(Number.NaN)).toThrow(TypeError)
  })

  it('mostra traço quando não há valor', () => {
    expect(formatCentsOrDash(null)).toBe('—')
    expect(formatCentsOrDash(undefined)).toBe('—')
    expect(formatCentsOrDash(0)).toBe(`R$${NBSP}0,00`)
  })
})

describe('centsToInput', () => {
  it('não leva símbolo, para preencher formulários', () => {
    expect(centsToInput(35_000_000)).toBe('350.000,00')
  })
})

describe('parseMoneyToCents', () => {
  it.each([
    ['1234,56', 123456],
    ['1.234,56', 123456],
    ['R$ 1.234,56', 123456],
    [`R$${NBSP}1.234,56`, 123456],
    ['  650 ', 65000],
    ['0,1', 10],
    ['0,01', 1],
    ['0,10', 10],
    ['33,33', 3333],
    ['1.000.000', 100_000_000],
    ['0', 0],
    ['007,50', 750],
  ])('"%s" -> %i centavos', (text, cents) => {
    expect(parseMoneyToCents(text)).toBe(cents)
  })

  it.each(['', 'abc', '1,234', '1.23', '12.34,56', '1,2,3', '-10,00', '10.', ',50', '1e3'])(
    'recusa "%s"',
    (text) => {
      expect(parseMoneyToCents(text)).toBeNull()
    },
  )

  it('33,33 três vezes soma exatamente 99,99 (nenhum centavo some ou aparece)', () => {
    const total = [1, 2, 3].reduce((sum) => sum + (parseMoneyToCents('33,33') ?? 0), 0)
    expect(total).toBe(9999)
    expect(formatCents(total)).toBe(`R$${NBSP}99,99`)
  })

  it('ida e volta preserva o valor', () => {
    for (const cents of [0, 1, 99, 100, 123456, 987654321, 10 ** 13]) {
      expect(parseMoneyToCents(centsToInput(cents))).toBe(cents)
    }
  })

  it('recusa acima do limite da API', () => {
    expect(parseMoneyToCents('100.000.000.000,01')).toBeNull()
    expect(parseMoneyToCents('999999999999999999')).toBeNull()
  })
})
