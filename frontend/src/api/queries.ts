// Hooks de dados (TanStack Query). Cada consulta tem uma chave; depois de salvar algo,
// as chaves afetadas são invalidadas e as telas que usam esses dados buscam de novo.

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type {
  Balance,
  Commitments,
  Dashboard,
  Expense,
  ExpenseFields,
  Financing,
  FinancingFields,
  Payment,
  PropertyDetail,
  PropertyFields,
  PropertySummary,
  SourceKind,
  Valuation,
} from '@/api/types'
import type { YearMonth } from '@/lib/dates'

export const queryKeys = {
  properties: ['properties'] as const,
  property: (id: number) => ['properties', id] as const,
  dashboard: ['dashboard'] as const,
  commitments: (period: YearMonth) => ['commitments', period.year, period.month] as const,
}

/** Qualquer mudança em imóveis, registros ou pagamentos afeta estas telas. */
function useInvalidatePortfolio() {
  const queryClient = useQueryClient()
  return () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.properties }),
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
      queryClient.invalidateQueries({ queryKey: ['commitments'] }),
    ])
}

function useSaveMutation<TInput, TResult>(request: (input: TInput) => Promise<TResult>) {
  const invalidate = useInvalidatePortfolio()
  return useMutation({ mutationFn: request, onSuccess: invalidate })
}

// --- leituras ---

export function useProperties() {
  return useQuery({
    queryKey: queryKeys.properties,
    queryFn: () => api.get<PropertySummary[]>('/properties'),
  })
}

export function useProperty(id: number) {
  return useQuery({
    queryKey: queryKeys.property(id),
    queryFn: () => api.get<PropertyDetail>(`/properties/${id}`),
  })
}

export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: () => api.get<Dashboard>('/dashboard'),
  })
}

export function useCommitments(period: YearMonth | null) {
  const query = period ? `?year=${period.year}&month=${period.month}` : ''
  return useQuery({
    queryKey: period ? queryKeys.commitments(period) : ['commitments', 'current'],
    queryFn: () => api.get<Commitments>(`/commitments${query}`),
  })
}

// --- demonstração ---

/** Só chamado quando `session.is_demo` é true (veja AppLayout). Apaga e recria a carteira. */
export function useResetDemo() {
  return useSaveMutation(() => api.post<null>('/demo/reset', {}))
}

// --- imóveis ---

export function useCreateProperty() {
  return useSaveMutation((fields: PropertyFields) =>
    api.post<PropertyDetail>('/properties', fields),
  )
}

export function useUpdateProperty(id: number) {
  return useSaveMutation((fields: Partial<PropertyFields>) =>
    api.patch<PropertyDetail>(`/properties/${id}`, fields),
  )
}

export function useDeleteProperty() {
  return useSaveMutation((id: number) => api.delete(`/properties/${id}`))
}

// --- registros ligados ao imóvel ---

export type ValuationFields = Omit<Valuation, 'id' | 'property_id'>
export type BalanceFields = Omit<Balance, 'id' | 'financing_id'>

/** Cria (sem id) ou edita (com id) um registro filho. */
function childMutation<TFields, TResult>(createPath: string, itemPath: string) {
  return ({ id, fields }: { id?: number; fields: TFields }) =>
    id === undefined
      ? api.post<TResult>(createPath, fields)
      : api.patch<TResult>(`${itemPath}/${id}`, fields)
}

export function useSaveValuation(propertyId: number) {
  return useSaveMutation(
    childMutation<ValuationFields, Valuation>(
      `/properties/${propertyId}/valuations`,
      '/valuations',
    ),
  )
}

export function useSaveFinancing(propertyId: number) {
  return useSaveMutation(
    childMutation<FinancingFields, Financing>(
      `/properties/${propertyId}/financings`,
      '/financings',
    ),
  )
}

export function useSaveBalance(financingId: number) {
  return useSaveMutation(
    childMutation<BalanceFields, Balance>(`/financings/${financingId}/balances`, '/balances'),
  )
}

export function useSaveExpense(propertyId: number) {
  return useSaveMutation(
    childMutation<ExpenseFields, Expense>(`/properties/${propertyId}/expenses`, '/expenses'),
  )
}

export type RecordKind = 'valuations' | 'financings' | 'balances' | 'expenses' | 'payments'

export function useDeleteRecord() {
  return useSaveMutation(({ kind, id }: { kind: RecordKind; id: number }) =>
    api.delete(`/${kind}/${id}`),
  )
}

// --- pagamentos ---

export interface NewPayment {
  source_kind: SourceKind
  source_id: number
  reference_due_date: string
  payment_date: string
  amount_paid_cents: number
}

export function useCreatePayment() {
  return useSaveMutation((payment: NewPayment) => api.post<Payment>('/payments', payment))
}
