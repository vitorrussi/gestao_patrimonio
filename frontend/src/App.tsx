import { useEffect, useState } from 'react'

interface HealthResponse {
  status: string
  database: string | null
}

type HealthState =
  | { kind: 'carregando' }
  | { kind: 'ok'; data: HealthResponse }
  | { kind: 'erro'; message: string }

function App() {
  const [health, setHealth] = useState<HealthState>({ kind: 'carregando' })

  useEffect(() => {
    let cancelado = false

    fetch('/api/health')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`resposta ${response.status}`)
        }
        return response.json() as Promise<HealthResponse>
      })
      .then((data) => {
        if (!cancelado) setHealth({ kind: 'ok', data })
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : String(error)
        if (!cancelado) setHealth({ kind: 'erro', message })
      })

    return () => {
      cancelado = true
    }
  }, [])

  return (
    <main>
      <h1>Gestão de Patrimônio</h1>
      {health.kind === 'carregando' && <p>Carregando status da API…</p>}
      {health.kind === 'ok' && (
        <p>
          API: {health.data.status} — banco: {health.data.database ?? 'sem dado'}
        </p>
      )}
      {health.kind === 'erro' && <p>Falha ao consultar a API: {health.message}</p>}
    </main>
  )
}

export default App
