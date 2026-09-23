// Peças de formulário: rótulo + campo + mensagem de erro, select de enum e checkbox.

import type { ReactNode } from 'react'
import {
  type Control,
  Controller,
  type FieldValues,
  type Path,
  type UseFormReturn,
} from 'react-hook-form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'

interface FieldRowProps {
  id: string
  label: string
  error?: string
  hint?: string
  className?: string
  children: ReactNode
}

export function FieldRow({ id, label, error, hint, className, children }: FieldRowProps) {
  return (
    <div className={cn('grid gap-1.5', className)}>
      <Label htmlFor={id}>{label}</Label>
      {children}
      {hint && !error && <p className="text-xs text-muted-foreground">{hint}</p>}
      {error && (
        <p id={`${id}-error`} role="alert" className="text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}

export function FormErrorBanner({ message }: { message?: string | null }) {
  if (!message) return null
  return (
    <p role="alert" className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
      {message}
    </p>
  )
}

interface EnumSelectProps<T extends FieldValues> {
  id: string
  name: Path<T>
  control: Control<T>
  options: { value: string; label: string }[]
  placeholder?: string
  invalid?: boolean
  disabled?: boolean
}

/** Select do shadcn ligado ao React Hook Form (o Controller faz a ponte). */
export function EnumSelect<T extends FieldValues>({
  id,
  name,
  control,
  options,
  placeholder = 'Selecione',
  invalid,
  disabled,
}: EnumSelectProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <Select value={field.value || undefined} onValueChange={field.onChange} disabled={disabled}>
          <SelectTrigger id={id} className="w-full" aria-invalid={invalid || undefined}>
            <SelectValue placeholder={placeholder} />
          </SelectTrigger>
          <SelectContent>
            {options.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
    />
  )
}

interface CheckboxRowProps extends React.ComponentProps<'input'> {
  label: string
}

export function CheckboxRow({ id, label, ...props }: CheckboxRowProps) {
  return (
    <label htmlFor={id} className="flex items-center gap-2 text-sm">
      <input id={id} type="checkbox" className="size-4 accent-primary" {...props} />
      {label}
    </label>
  )
}

interface FormInputProps<T extends FieldValues> {
  form: UseFormReturn<T>
  name: Path<T>
  label: string
  hint?: string
  className?: string
  inputProps?: React.ComponentProps<'input'>
}

/** Campo de texto ligado ao React Hook Form, com rótulo e erro. */
export function FormInput<T extends FieldValues>({
  form,
  name,
  label,
  hint,
  className,
  inputProps,
}: FormInputProps<T>) {
  const error = form.getFieldState(name, form.formState).error?.message
  return (
    <FieldRow id={name} label={label} error={error} hint={hint} className={className}>
      <Input
        id={name}
        aria-invalid={error ? true : undefined}
        {...inputProps}
        className={cn('read-only:bg-muted read-only:text-muted-foreground', inputProps?.className)}
        {...form.register(name)}
      />
    </FieldRow>
  )
}

interface FormSelectProps<T extends FieldValues> {
  form: UseFormReturn<T>
  name: Path<T>
  label: string
  options: { value: string; label: string }[]
  hint?: string
  disabled?: boolean
}

export function FormSelect<T extends FieldValues>({
  form,
  name,
  label,
  options,
  hint,
  disabled,
}: FormSelectProps<T>) {
  const error = form.getFieldState(name, form.formState).error?.message
  return (
    <FieldRow id={name} label={label} error={error} hint={hint}>
      <EnumSelect
        id={name}
        name={name}
        control={form.control}
        options={options}
        invalid={!!error}
        disabled={disabled}
      />
    </FieldRow>
  )
}
