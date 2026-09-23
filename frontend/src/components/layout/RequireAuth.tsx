// Portão das rotas logadas: sem sessão, manda para /login (e volta para cá depois).

import { Navigate, Outlet, useLocation } from 'react-router'
import { LoadingState, QueryErrorState } from '@/components/display'
import { useSession } from '@/features/auth/session'

export function RequireAuth() {
  const session = useSession()
  const location = useLocation()

  if (session.isPending) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <LoadingState />
      </div>
    )
  }
  if (session.isError) {
    return (
      <div className="mx-auto max-w-6xl p-6">
        <QueryErrorState error={session.error} onRetry={() => void session.refetch()} />
      </div>
    )
  }
  if (!session.data) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}
