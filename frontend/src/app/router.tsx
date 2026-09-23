// Tabela de rotas: endereço -> página. Tudo abaixo de RequireAuth exige login.
// As páginas carregam sob demanda (`lazy`): cada uma vira um arquivo JS separado,
// baixado só quando a rota é aberta.

import { createBrowserRouter } from 'react-router'
import { NotFoundPage } from '@/components/NotFoundPage'
import { AppLayout } from '@/components/layout/AppLayout'
import { RequireAuth } from '@/components/layout/RequireAuth'

export const router = createBrowserRouter([
  {
    path: '/login',
    lazy: () => import('@/features/auth/AuthPages').then((m) => ({ Component: m.LoginPage })),
  },
  {
    path: '/cadastro',
    lazy: () => import('@/features/auth/AuthPages').then((m) => ({ Component: m.RegisterPage })),
  },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            index: true,
            lazy: () =>
              import('@/features/dashboard/DashboardPage').then((m) => ({
                Component: m.DashboardPage,
              })),
          },
          {
            path: 'imoveis',
            lazy: () =>
              import('@/features/properties/PropertyListPage').then((m) => ({
                Component: m.PropertyListPage,
              })),
          },
          {
            path: 'imoveis/novo',
            lazy: () =>
              import('@/features/properties/PropertyFormPage').then((m) => ({
                Component: m.NewPropertyPage,
              })),
          },
          {
            path: 'imoveis/:id',
            lazy: () =>
              import('@/features/properties/PropertyDetailPage').then((m) => ({
                Component: m.PropertyDetailPage,
              })),
          },
          {
            path: 'imoveis/:id/editar',
            lazy: () =>
              import('@/features/properties/PropertyFormPage').then((m) => ({
                Component: m.EditPropertyPage,
              })),
          },
          {
            path: 'compromissos',
            lazy: () =>
              import('@/features/commitments/CommitmentsPage').then((m) => ({
                Component: m.CommitmentsPage,
              })),
          },
          {
            path: 'ajuda',
            lazy: () => import('@/features/help/HelpPage').then((m) => ({ Component: m.HelpPage })),
          },
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
])
