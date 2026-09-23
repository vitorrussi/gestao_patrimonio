// Modo "novo" mantém o payload de sempre; modo "existente" pede prazo restante + saldo
// devedor inicial e, ao salvar, lança os dois registros (financiamento e saldo).

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'
import { FinancingDialog } from './FinancingDialog'

beforeAll(() => {
  // jsdom não implementa isso; o Radix Select usa no fluxo de abrir/fechar o menu.
  Element.prototype.hasPointerCapture = () => false
  Element.prototype.scrollIntoView = () => {}
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function mockApi(responses: { status: number; body: unknown }[]) {
  let call = 0
  const fetchMock = vi.fn((_url: string, _init: RequestInit) => {
    const response = responses[Math.min(call, responses.length - 1)]
    call += 1
    return Promise.resolve(new Response(JSON.stringify(response.body), { status: response.status }))
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

function renderDialog(onClose = vi.fn()) {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <FinancingDialog propertyId={3} onClose={onClose} />
    </QueryClientProvider>,
  )
  return onClose
}

async function selectOption(label: string, optionLabel: string) {
  await userEvent.click(screen.getByLabelText(label))
  await userEvent.click(await screen.findByRole('option', { name: optionLabel }))
}

async function fillContractFields() {
  await userEvent.type(screen.getByLabelText('Credor'), 'Caixa')
  await userEvent.type(screen.getByLabelText('Valor financiado (R$)'), '300.000,00')
  await userEvent.type(screen.getByLabelText('Parcela atual (R$)'), '1.500,00')
  await selectOption('Sistema de amortização', 'SAC')
  await selectOption('Indexador', 'TR')
  await userEvent.type(screen.getByLabelText('Juros ao ano (%)'), '9,5')
}

describe('FinancingDialog', () => {
  it('modo novo: envia só os campos do financiamento, sem saldo inicial', async () => {
    const fetchMock = mockApi([{ status: 201, body: { id: 1, property_id: 3 } }])
    const onClose = renderDialog()

    expect(screen.queryByLabelText('Saldo devedor atual (R$)')).toBeNull()

    await fillContractFields()
    await userEvent.type(screen.getByLabelText('Prazo total (meses)'), '240')
    fireEvent.change(screen.getByLabelText('Data da 1ª parcela'), {
      target: { value: '2026-10-05' },
    })
    await userEvent.type(screen.getByLabelText('Dia de vencimento'), '5')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))

    await waitFor(() => expect(onClose).toHaveBeenCalled())
    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/properties/3/financings')
    const body: unknown = JSON.parse(init.body as string)
    expect(body).not.toHaveProperty('mode')
    expect(body).not.toHaveProperty('initial_debt_balance')
    expect(body).toHaveProperty('term_months', 240)
  })

  it('modo existente: pede prazo restante e saldo devedor, e lança os dois registros', async () => {
    const fetchMock = mockApi([
      { status: 201, body: { id: 42, property_id: 3 } },
      { status: 201, body: { id: 1, financing_id: 42 } },
    ])
    const onClose = renderDialog()

    await selectOption('Situação do financiamento', 'Financiamento já em andamento')
    expect(screen.getByLabelText('Prazo restante (meses)')).toBeTruthy()
    expect(screen.getByLabelText('Data da próxima parcela')).toBeTruthy()

    await fillContractFields()
    await userEvent.type(screen.getByLabelText('Prazo restante (meses)'), '140')
    fireEvent.change(screen.getByLabelText('Data da próxima parcela'), {
      target: { value: '2026-10-05' },
    })
    await userEvent.type(screen.getByLabelText('Dia de vencimento'), '5')
    fireEvent.change(screen.getByLabelText('Data do saldo devedor'), {
      target: { value: '2026-09-20' },
    })
    await userEvent.type(screen.getByLabelText('Saldo devedor atual (R$)'), '180.000,00')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))

    await waitFor(() => expect(onClose).toHaveBeenCalled())
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))

    const [financingUrl, financingInit] = fetchMock.mock.calls[0]
    expect(financingUrl).toBe('/api/properties/3/financings')
    const financingBody: unknown = JSON.parse(financingInit.body as string)
    expect(financingBody).not.toHaveProperty('mode')
    expect(financingBody).not.toHaveProperty('initial_debt_balance')
    expect(financingBody).toHaveProperty('term_months', 140)

    const [balanceUrl, balanceInit] = fetchMock.mock.calls[1]
    expect(balanceUrl).toBe('/api/financings/42/balances')
    expect(JSON.parse(balanceInit.body as string)).toEqual({
      balance_date: '2026-09-20',
      balance_cents: 18000000,
    })
  })

  it('modo existente sem saldo devedor: não envia nada e explica o motivo', async () => {
    const fetchMock = mockApi([{ status: 201, body: {} }])
    renderDialog()

    await selectOption('Situação do financiamento', 'Financiamento já em andamento')
    await fillContractFields()
    await userEvent.type(screen.getByLabelText('Prazo restante (meses)'), '140')
    fireEvent.change(screen.getByLabelText('Data da próxima parcela'), {
      target: { value: '2026-10-05' },
    })
    await userEvent.type(screen.getByLabelText('Dia de vencimento'), '5')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))

    expect(
      await screen.findByText(
        'Informe o saldo devedor atual (sem ele, a dívida aparece como o valor financiado total).',
      ),
    ).toBeTruthy()
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
