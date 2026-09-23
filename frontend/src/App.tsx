import { useEffect, useState } from 'react'

interface HealthResponse {
  status: string
  database: string | null
}

type HealthState =
  { kind: 'loading' } | { kind: 'ok'; data: HealthResponse } | { kind: 'error'; message: string }

function App() {
  const [health, setHealth] = useState<HealthState>({ kind: 'loading' })

  useEffect(() => {
    let cancelled = false

    fetch('/api/health')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`resposta ${response.status}`)
        }
        return response.json() as Promise<HealthResponse>
      })
      .then((data) => {
        if (!cancelled) setHealth({ kind: 'ok', data })
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : String(error)
        if (!cancelled) setHealth({ kind: 'error', message })
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main>
      <h1>Gestão de Patrimônio</h1>
      {health.kind === 'loading' && <p>Carregando status da API…</p>}
      {health.kind === 'ok' && (
        <p>
          API: {health.data.status} — banco: {health.data.database ?? 'sem dado'}
        </p>
      )}
      {health.kind === 'error' && <p>Falha ao consultar a API: {health.message}</p>}
    </main>
  )
}

export default App
