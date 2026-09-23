import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api } from '@/api/client'
import { errorMessage, fieldErrors } from './apiErrors'

afterEach(() => {
  vi.unstubAllGlobals()
})

function validationError(details: { field: string | null; type: string; message: string }[]) {
  return new ApiError(400, { error: 'validation_error', details })
}

describe('errorMessage', () => {
  it('traduz códigos conhecidos', () => {
    expect(errorMessage(new ApiError(409, { error: 'payment_already_registered' }))).toBe(
      'Este vencimento já tem pagamento registrado.',
    )
    expect(errorMessage(new ApiError(401, { error: 'invalid_credentials' }))).toBe(
      'E-mail ou senha inválidos.',
    )
  })

  it('usa a mensagem em português da trava de regra', () => {
    const error = new ApiError(409, {
      error: 'rule_locked_by_payments',
      message: 'Já existem pagamentos para esta regra.',
      fields: ['due_day'],
    })
    expect(errorMessage(error)).toBe('Já existem pagamentos para esta regra.')
  })

  it('mostra erro geral de validação (sem campo) escrito pela API', () => {
    const error = validationError([
      {
        field: null,
        type: 'value_error',
        message: 'Value error, a data de fim não pode ser anterior',
      },
    ])
    expect(errorMessage(error)).toBe('A data de fim não pode ser anterior.')
  })

  it('cai numa mensagem genérica para erro desconhecido ou falha de rede', () => {
    expect(errorMessage(new ApiError(500, null))).toBe('Algo deu errado. Tente de novo.')
    expect(errorMessage(new TypeError('Failed to fetch'))).toMatch(/servidor/)
  })
})

describe('fieldErrors', () => {
  it('traduz pelo type e nunca mostra a mensagem em inglês do Pydantic', () => {
    const error = validationError([
      {
        field: 'nickname',
        type: 'string_too_short',
        message: 'String should have at least 1 character',
      },
      {
        field: 'due_day',
        type: 'less_than_equal',
        message: 'Input should be less than or equal to 31',
      },
      { field: 'state', type: 'value_error', message: 'Value error, UF com 2 letras, ex.: SC' },
    ])

    expect(fieldErrors(error)).toEqual({
      nickname: 'Campo obrigatório.',
      due_day: 'Valor acima do máximo.',
      state: 'UF com 2 letras, ex.: SC.',
    })
  })

  it('não devolve nada para erros que não são de validação', () => {
    expect(fieldErrors(new ApiError(404, { error: 'not_found' }))).toEqual({})
  })
})

describe('apiRequest', () => {
  it('lança ApiError com status e corpo da resposta', async () => {
    const body = JSON.stringify({ error: 'not_found' })
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(new Response(body, { status: 404 }))),
    )

    await expect(api.get('/properties/1')).rejects.toMatchObject({ status: 404, code: 'not_found' })
  })

  it('devolve null em 204 e envia JSON no corpo', async () => {
    const fetchMock = vi.fn((_url: string, _init: RequestInit) =>
      Promise.resolve(new Response(null, { status: 204 })),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(api.post('/payments', { amount_paid_cents: 100 })).resolves.toBeNull()
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/payments')
    expect(init.body).toBe('{"amount_paid_cents":100}')
  })

  it('trata resposta que não é JSON como corpo vazio', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(new Response('<html>', { status: 502 }))),
    )

    await expect(api.get('/dashboard')).rejects.toMatchObject({
      status: 502,
      code: 'unknown_error',
    })
  })
})
