// Sessão: GET /api/auth/me diz quem está logado (401 = ninguém). O resultado fica no
// cache sob a chave ["session"]; login e logout atualizam essa chave diretamente.

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, api } from '@/api/client'
import type { User } from '@/api/types'

const SESSION_KEY = ['session'] as const

export interface Credentials {
  email: string
  password: string
}

async function fetchSession(): Promise<User | null> {
  try {
    return await api.get<User>('/auth/me')
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null
    throw error
  }
}

export function useSession() {
  return useQuery({ queryKey: SESSION_KEY, queryFn: fetchSession, staleTime: Infinity })
}

function useSessionMutation(request: (credentials: Credentials) => Promise<User>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: request,
    onSuccess: (user) => {
      queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== SESSION_KEY[0] })
      queryClient.setQueryData(SESSION_KEY, user)
    },
  })
}

export function useLogin() {
  return useSessionMutation((credentials) => api.post<User>('/auth/login', credentials))
}

export function useRegister() {
  return useSessionMutation((credentials) => api.post<User>('/auth/register', credentials))
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => api.post<null>('/auth/logout', {}),
    onSettled: () => {
      // Limpa tudo: dados de um usuário nunca ficam visíveis para o próximo.
      queryClient.clear()
      queryClient.setQueryData(SESSION_KEY, null)
    },
  })
}
