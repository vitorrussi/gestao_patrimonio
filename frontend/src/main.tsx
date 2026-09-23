// Ponto de entrada: liga o cache de dados (TanStack Query), as rotas e os avisos (toasts).

import { QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router'
import { createQueryClient } from '@/app/queryClient'
import { router } from '@/app/router'
import { Toaster } from '@/components/ui/sonner'
import './index.css'

const queryClient = createQueryClient()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster position="top-center" richColors={false} />
    </QueryClientProvider>
  </StrictMode>,
)
