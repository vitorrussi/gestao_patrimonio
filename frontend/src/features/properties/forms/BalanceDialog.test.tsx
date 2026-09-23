// Do texto digitado ao corpo enviado à API: "1.234,56" precisa chegar como 123456 centavos.

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { BalanceDialog } from './SimpleRecordDialogs'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function mockApi(status: number, body: unknown) {
  const fetchMock = vi.fn((_url: string, _init: RequestInit) =>
    Promise.resolve(new Response(JSON.stringify(body), { status })),
  )
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

function renderDialog(onClose = vi.fn()) {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <BalanceDialog financingId={7} onClose={onClose} />
    </QueryClientProvider>,
  )
  return onClose
}

async function fillAndSubmit(date: string, amount: string) {
  fireEvent.change(screen.getByLabelText('Data do extrato'), { target: { value: date } })
  await userEvent.type(screen.getByLabelText('Saldo devedor (R$)'), amount)
  await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))
}

describe('BalanceDialog', () => {
  it('envia o valor em centavos inteiros e fecha', async () => {
    const fetchMock = mockApi(201, { id: 1, financing_id: 7 })
    const onClose = renderDialog()

    await fillAndSubmit('2026-08-31', '1.234,56')

    await waitFor(() => expect(onClose).toHaveBeenCalled())
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/financings/7/balances')
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body as string)).toEqual({
      balance_date: '2026-08-31',
      balance_cents: 123456,
    })
  })

  it('não envia valor inválido e explica o formato', async () => {
    const fetchMock = mockApi(201, {})
    renderDialog()

    await fillAndSubmit('2026-08-31', '1,234')

    expect(await screen.findByText('Valor inválido. Ex.: 1.234,56')).toBeTruthy()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('mostra no campo o erro devolvido pela API, em português', async () => {
    mockApi(400, {
      error: 'validation_error',
      details: [
        {
          field: 'balance_cents',
          type: 'less_than_equal',
          message: 'Input should be less than or equal to 10000000000000',
        },
      ],
    })
    const onClose = renderDialog()

    await fillAndSubmit('2026-08-31', '10,00')

    expect(await screen.findByText('Valor acima do máximo.')).toBeTruthy()
    expect(screen.queryByText(/Input should/)).toBeNull()
    expect(onClose).not.toHaveBeenCalled()
  })
})
