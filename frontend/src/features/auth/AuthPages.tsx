// Telas de login e cadastro (mesmo formulário, textos e regras diferentes).

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { z } from 'zod'
import { FieldRow, FormErrorBanner } from '@/components/form'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { errorMessage } from '@/lib/apiErrors'
import { looksLikeEmail } from '@/lib/formFields'
import { type Credentials, useLogin, useRegister, useSession } from './session'

const loginSchema = z.object({
  email: z.string().trim().min(1, 'Informe o e-mail.'),
  password: z.string().min(1, 'Informe a senha.'),
})

const registerSchema = z.object({
  email: z.string().trim().refine(looksLikeEmail, 'E-mail inválido.'),
  password: z
    .string()
    .min(8, 'A senha precisa ter pelo menos 8 caracteres.')
    .max(128, 'A senha pode ter no máximo 128 caracteres.'),
})

type Mode = 'login' | 'register'

const MODES = {
  login: {
    schema: loginSchema,
    title: 'Entrar',
    submitLabel: 'Entrar',
    passwordAutoComplete: 'current-password',
    passwordHint: undefined,
    switchText: 'Ainda não tem conta? ',
    switchLink: { to: '/cadastro', label: 'Cadastre-se' },
  },
  register: {
    schema: registerSchema,
    title: 'Criar conta',
    submitLabel: 'Criar conta',
    passwordAutoComplete: 'new-password',
    passwordHint: 'Mínimo de 8 caracteres.',
    switchText: 'Já tem conta? ',
    switchLink: { to: '/login', label: 'Entre' },
  },
} as const

interface AuthFormProps {
  mode: Mode
}

function useAuthMutation(mode: Mode) {
  const login = useLogin()
  const register = useRegister()
  return mode === 'login' ? login : register
}

function AuthForm({ mode }: AuthFormProps) {
  const config = MODES[mode]
  const mutation = useAuthMutation(mode)
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: string } | null)?.from ?? '/'

  const form = useForm<Credentials>({
    resolver: zodResolver(config.schema),
    defaultValues: { email: '', password: '' },
  })
  const { errors } = form.formState

  const onSubmit = form.handleSubmit((credentials) => {
    mutation.mutate(credentials, { onSuccess: () => void navigate(from, { replace: true }) })
  })

  return (
    <form onSubmit={(event) => void onSubmit(event)} className="grid gap-4" noValidate>
      <FormErrorBanner message={mutation.isError ? errorMessage(mutation.error) : null} />
      <FieldRow id="email" label="E-mail" error={errors.email?.message}>
        <Input id="email" type="email" autoComplete="email" {...form.register('email')} />
      </FieldRow>
      <FieldRow
        id="password"
        label="Senha"
        error={errors.password?.message}
        hint={config.passwordHint}
      >
        <Input
          id="password"
          type="password"
          autoComplete={config.passwordAutoComplete}
          {...form.register('password')}
        />
      </FieldRow>
      <Button type="submit" disabled={mutation.isPending}>
        {config.submitLabel}
      </Button>
    </form>
  )
}

function AuthPage({ mode }: AuthFormProps) {
  const session = useSession()
  if (session.data) return <Navigate to="/" replace />
  const config = MODES[mode]

  return (
    <div className="flex min-h-svh items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>{config.title}</CardTitle>
          <CardDescription>Gestão de Patrimônio</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <AuthForm mode={mode} />
          <p className="text-center text-sm text-muted-foreground">
            {config.switchText}
            <Link to={config.switchLink.to} className="text-primary underline">
              {config.switchLink.label}
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export function LoginPage() {
  return <AuthPage mode="login" />
}

export function RegisterPage() {
  return <AuthPage mode="register" />
}
