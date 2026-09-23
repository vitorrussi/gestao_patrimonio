// Moldura das telas logadas: cabeçalho com menu (no celular, menu em gaveta lateral).

import { Building2, CalendarClock, LayoutDashboard, LogOut, Menu, RotateCcw } from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router'
import { toast } from 'sonner'
import { useResetDemo } from '@/api/queries'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { useLogout, useSession } from '@/features/auth/session'
import { errorMessage } from '@/lib/apiErrors'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { to: '/', label: 'Painel', icon: LayoutDashboard, end: true },
  { to: '/imoveis', label: 'Imóveis', icon: Building2, end: false },
  { to: '/compromissos', label: 'Compromissos', icon: CalendarClock, end: false },
]

function NavLinks({ onNavigate, vertical }: { onNavigate?: () => void; vertical?: boolean }) {
  return (
    <nav className={cn('flex gap-1', vertical && 'flex-col')}>
      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground',
              isActive && 'bg-muted font-medium text-foreground',
            )
          }
        >
          <Icon className="size-4" />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

function ResetDemoButton() {
  const reset = useResetDemo()
  const handleReset = () => {
    reset.mutate(undefined, {
      onSuccess: () => toast.success('Dados de demonstração restaurados.'),
      onError: (error) => toast.error(errorMessage(error)),
    })
  }
  return (
    <ConfirmDialog
      trigger={
        <Button variant="outline" size="sm" disabled={reset.isPending}>
          <RotateCcw className="size-4" />
          Restaurar padrão
        </Button>
      }
      title="Restaurar dados de demonstração?"
      description="Apaga tudo o que foi editado neste demo e recria a carteira fictícia original. O app real não é afetado."
      confirmLabel="Restaurar"
      onConfirm={handleReset}
    />
  )
}

function LogoutButton() {
  const logout = useLogout()
  const navigate = useNavigate()
  const handleLogout = () => {
    logout.mutate(undefined, { onSettled: () => void navigate('/login', { replace: true }) })
  }
  return (
    <Button variant="ghost" size="sm" onClick={handleLogout} disabled={logout.isPending}>
      <LogOut className="size-4" />
      Sair
    </Button>
  )
}

export function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const session = useSession()

  return (
    <div className="min-h-svh bg-background">
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4">
          <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden" aria-label="Abrir menu">
                <Menu className="size-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64">
              <SheetHeader>
                <SheetTitle>Gestão de Patrimônio</SheetTitle>
              </SheetHeader>
              <div className="px-4">
                <NavLinks vertical onNavigate={() => setMenuOpen(false)} />
              </div>
            </SheetContent>
          </Sheet>
          <span className="font-heading font-semibold">Gestão de Patrimônio</span>
          <div className="hidden md:block">
            <NavLinks />
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="hidden text-sm text-muted-foreground sm:inline">
              {session.data?.email}
            </span>
            {session.data?.is_demo && <ResetDemoButton />}
            <LogoutButton />
          </div>
        </div>
      </header>
      <main className="mx-auto grid max-w-6xl gap-6 px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
