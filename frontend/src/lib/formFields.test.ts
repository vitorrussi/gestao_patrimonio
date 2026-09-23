import { describe, expect, it } from 'vitest'
import { looksLikeEmail, requiredMoney, toCents, toOptionalCents, toPercent } from './formFields'

describe('looksLikeEmail', () => {
  it.each([
    ['dono@example.com', true],
    ['a@b.co', true],
    ['sem-arroba', false],
    ['a@b', false],
    ['a b@c.com', false],
    ['a@@b.com', false],
    ['@b.com', false],
    ['a@.com', false],
    ['a@b.', false],
  ])('%s -> %s', (text, valid) => {
    expect(looksLikeEmail(text)).toBe(valid)
  })
})

describe('conversões do envio', () => {
  it('converte dinheiro digitado para centavos', () => {
    expect(toCents('1.234,56')).toBe(123456)
    expect(toOptionalCents('')).toBe(0)
    expect(toOptionalCents('7.000')).toBe(700000)
  })

  it('recusa converter valor que não passou pela validação', () => {
    expect(() => toCents('abc')).toThrow()
    expect(() => toPercent('150', 100)).toThrow()
  })

  it('valida dinheiro com mensagem em português', () => {
    const result = requiredMoney.safeParse('1,234')
    expect(result.success).toBe(false)
    expect(result.error?.issues[0].message).toBe('Valor inválido. Ex.: 1.234,56')
  })
})
