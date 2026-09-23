// Páginas de cadastro (/imoveis/novo) e edição (/imoveis/:id/editar) do imóvel.

import { useNavigate, useParams } from 'react-router'
import { toast } from 'sonner'
import { useCreateProperty, useProperty, useUpdateProperty } from '@/api/queries'
import { LoadingState, PageHeader, QueryErrorState } from '@/components/display'
import { errorMessage } from '@/lib/apiErrors'
import { applyServerErrors } from '@/lib/formFields'
import { PropertyForm } from './PropertyForm'
import { EMPTY_PROPERTY, formToProperty, propertyToForm } from './propertySchema'

export function NewPropertyPage() {
  const create = useCreateProperty()
  const navigate = useNavigate()

  return (
    <>
      <PageHeader title="Novo imóvel" />
      <PropertyForm
        defaultValues={EMPTY_PROPERTY}
        submitLabel="Cadastrar"
        isEdit={false}
        isPending={create.isPending}
        errorMessage={create.isError ? errorMessage(create.error) : null}
        onCancel={() => void navigate('/imoveis')}
        onSubmit={(values, form) =>
          create.mutate(formToProperty(values), {
            onSuccess: (property) => {
              toast.success('Imóvel cadastrado.')
              void navigate(`/imoveis/${property.id}`)
            },
            onError: (error) => applyServerErrors(form.setError, error),
          })
        }
      />
    </>
  )
}

export function EditPropertyPage() {
  const id = Number(useParams().id)
  const property = useProperty(id)
  const update = useUpdateProperty(id)
  const navigate = useNavigate()

  if (property.isPending) return <LoadingState />
  if (property.isError) return <QueryErrorState error={property.error} />

  return (
    <>
      <PageHeader title={`Editar ${property.data.nickname}`} />
      <PropertyForm
        defaultValues={propertyToForm(property.data)}
        submitLabel="Salvar"
        isEdit
        isPending={update.isPending}
        errorMessage={update.isError ? errorMessage(update.error) : null}
        onCancel={() => void navigate(`/imoveis/${id}`)}
        onSubmit={(values, form) =>
          update.mutate(formToProperty(values), {
            onSuccess: () => {
              toast.success('Alterações salvas.')
              void navigate(`/imoveis/${id}`)
            },
            onError: (error) => applyServerErrors(form.setError, error),
          })
        }
      />
    </>
  )
}
