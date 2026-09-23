import type { ErrorBody, ErrorDetail } from '@/api/types'

/** Erro devolvido pela API (status HTTP + corpo padronizado). */
export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: ErrorDetail[]
  readonly body: ErrorBody | null

  constructor(status: number, body: ErrorBody | null) {
    super(body?.message ?? body?.error ?? `erro ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.code = body?.error ?? 'unknown_error'
    this.details = body?.details ?? []
    this.body = body
  }
}

type Method = 'GET' | 'POST' | 'PATCH' | 'DELETE'

function parseJson(text: string): unknown {
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    // Resposta que não é JSON (ex.: página de erro de um proxy): tratada como corpo vazio.
    return null
  }
}

export async function apiRequest<T>(method: Method, path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method,
    credentials: 'same-origin',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = parseJson(await response.text())
  if (!response.ok) {
    throw new ApiError(response.status, data as ErrorBody | null)
  }
  return data as T
}

export const api = {
  get: <T>(path: string) => apiRequest<T>('GET', path),
  post: <T>(path: string, body: unknown) => apiRequest<T>('POST', path, body),
  patch: <T>(path: string, body: unknown) => apiRequest<T>('PATCH', path, body),
  delete: (path: string) => apiRequest<null>('DELETE', path),
}
