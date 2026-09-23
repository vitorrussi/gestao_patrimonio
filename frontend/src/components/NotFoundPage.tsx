import { Link } from 'react-router'
import { EmptyState } from '@/components/display'
import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  return (
    <EmptyState
      message="Página não encontrada."
      action={
        <Button asChild variant="outline">
          <Link to="/">Voltar ao painel</Link>
        </Button>
      }
    />
  )
}
