import { describe, expect, it } from 'vitest'
import { apiPercentToInput, formatPercent, parsePercentInput } from './percent'

describe('apiPercentToInput / formatPercent', () => {
  it.each([
    ['100.0000', '100'],
    ['50.0000', '50'],
    ['33.3333', '33,3333'],
    ['9.5000', '9,5'],
    ['0.0000', '0'],
  ])('%s -> %s', (api, input) => {
    expect(apiPercentToInput(api)).toBe(input)
    expect(formatPercent(api)).toBe(`${input}%`)
  })
})

describe('parsePercentInput', () => {
  it.each([
    ['50', '50'],
    ['33,3333', '33.3333'],
    ['9.5', '9.5'],
    ['9,50', '9.50'],
    [' 100 ', '100'],
    ['100,0000', '100.0000'],
    ['050', '50'],
    ['12%', '12'],
  ])('"%s" -> "%s"', (text, api) => {
    expect(parsePercentInput(text, 100)).toBe(api)
  })

  it.each(['', 'abc', '100,01', '101', '33,33333', '-5', '1.000,5'])('recusa "%s"', (text) => {
    expect(parsePercentInput(text, 100)).toBeNull()
  })

  it('usa o máximo informado (taxa de juros aceita acima de 100)', () => {
    expect(parsePercentInput('150', 1000)).toBe('150')
    expect(parsePercentInput('1000,5', 1000)).toBeNull()
  })
})
