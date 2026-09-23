import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App.tsx'

function mockFetch(response: Response) {
  const fetchMock = vi.fn(() => Promise.resolve(response))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('mostra o status da API e o dado lido do banco', async () => {
    const fetchMock = mockFetch(Response.json({ status: 'ok', database: 'ok' }))

    render(<App />)

    expect(await screen.findByText('API: ok — banco: ok')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledWith('/api/health')
  })

  it('mostra a falha quando a API responde com erro', async () => {
    mockFetch(new Response(null, { status: 500 }))

    render(<App />)

    expect(await screen.findByText('Falha ao consultar a API: resposta 500')).toBeTruthy()
  })
})
