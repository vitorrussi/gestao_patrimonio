// Formulário do imóvel (cadastro e edição), dividido nas seções do ESCOPO 3.1.

import { MONEY_INPUT_PROPS } from '@/lib/formFields'
import { zodResolver } from '@hookform/resolvers/zod'
import { type UseFormReturn, useForm } from 'react-hook-form'
import { CheckboxRow, FormErrorBanner, FormInput, FormSelect } from '@/components/form'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { propertyHelp } from '@/features/help/content'
import {
  ACQUISITION_METHOD_LABELS,
  PROPERTY_TYPE_LABELS,
  PROPERTY_USAGE_LABELS,
  optionsOf,
} from '@/lib/labels'
import { type PropertyFormValues, propertySchema } from './propertySchema'

type Form = UseFormReturn<PropertyFormValues>

function IdentificationSection({ form }: { form: Form }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Identificação</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        <FormInput
          form={form}
          name="nickname"
          label="Apelido"
          help={propertyHelp.nickname}
          inputProps={{ placeholder: 'Ex.: Apto Centro' }}
        />
        <FormSelect
          form={form}
          name="property_type"
          label="Tipo"
          help={propertyHelp.property_type}
          options={optionsOf(PROPERTY_TYPE_LABELS)}
        />
        <FormSelect
          form={form}
          name="usage"
          label="Uso"
          help={propertyHelp.usage}
          options={optionsOf(PROPERTY_USAGE_LABELS)}
        />
      </CardContent>
    </Card>
  )
}

function StreetFields({ form }: { form: Form }) {
  return (
    <>
      <FormInput
        form={form}
        name="street"
        label="Logradouro"
        className="sm:col-span-4"
        help={propertyHelp.street}
      />
      <FormInput
        form={form}
        name="number"
        label="Número"
        className="sm:col-span-2"
        help={propertyHelp.number}
      />
      <FormInput
        form={form}
        name="complement"
        label="Complemento"
        className="sm:col-span-3"
        help={propertyHelp.complement}
      />
      <FormInput
        form={form}
        name="neighborhood"
        label="Bairro"
        className="sm:col-span-3"
        help={propertyHelp.neighborhood}
      />
    </>
  )
}

function CityFields({ form }: { form: Form }) {
  return (
    <>
      <FormInput
        form={form}
        name="city"
        label="Cidade"
        className="sm:col-span-3"
        help={propertyHelp.city}
      />
      <FormInput
        form={form}
        name="state"
        label="UF"
        className="sm:col-span-1"
        help={propertyHelp.state}
        inputProps={{ maxLength: 2 }}
      />
      <FormInput
        form={form}
        name="zip_code"
        label="CEP"
        className="sm:col-span-2"
        help={propertyHelp.zip_code}
        inputProps={{ inputMode: 'numeric', placeholder: '00000-000' }}
      />
    </>
  )
}

function AddressSection({ form }: { form: Form }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Endereço</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-6">
        <StreetFields form={form} />
        <CityFields form={form} />
      </CardContent>
    </Card>
  )
}

function DocumentsSection({ form }: { form: Form }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Documentação</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        <FormInput
          form={form}
          name="registration_number"
          label="Matrícula"
          help={propertyHelp.registration_number}
        />
        <FormInput
          form={form}
          name="registry_office"
          label="Cartório de registro"
          help={propertyHelp.registry_office}
        />
        <FormInput
          form={form}
          name="municipal_registration"
          label="Inscrição imobiliária (IPTU)"
          help={propertyHelp.municipal_registration}
        />
      </CardContent>
    </Card>
  )
}

function OwnershipSection({ form, showActive }: { form: Form; showActive: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Propriedade</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        <FormInput
          form={form}
          name="ownership_percentage"
          label="Participação (%)"
          help={propertyHelp.ownership_percentage}
          inputProps={{ inputMode: 'decimal' }}
        />
        <FormInput
          form={form}
          name="acquisition_date"
          label="Data de aquisição"
          help={propertyHelp.acquisition_date}
          inputProps={{ type: 'date' }}
        />
        <FormSelect
          form={form}
          name="acquisition_method"
          label="Forma de aquisição"
          help={propertyHelp.acquisition_method}
          options={optionsOf(ACQUISITION_METHOD_LABELS)}
        />
        {showActive && (
          <div className="sm:col-span-3">
            <CheckboxRow
              id="is_active"
              label="Imóvel ativo (desmarque quando for vendido)"
              help={propertyHelp.is_active}
              {...form.register('is_active')}
            />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function AcquisitionValuesSection({ form }: { form: Form }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Valores de aquisição</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        <FormInput
          form={form}
          name="purchase_price"
          label="Valor de compra (R$)"
          help={propertyHelp.purchase_price}
          inputProps={MONEY_INPUT_PROPS}
        />
        <FormInput
          form={form}
          name="itbi"
          label="ITBI (R$)"
          help={propertyHelp.itbi}
          inputProps={MONEY_INPUT_PROPS}
        />
        <FormInput
          form={form}
          name="deed_registration"
          label="Escritura e registro (R$)"
          help={propertyHelp.deed_registration}
          inputProps={MONEY_INPUT_PROPS}
        />
      </CardContent>
    </Card>
  )
}

interface PropertyFormProps {
  defaultValues: PropertyFormValues
  submitLabel: string
  isEdit: boolean
  isPending: boolean
  errorMessage: string | null
  onSubmit: (values: PropertyFormValues, form: Form) => void
  onCancel: () => void
}

export function PropertyForm(props: PropertyFormProps) {
  const form = useForm<PropertyFormValues>({
    resolver: zodResolver(propertySchema),
    defaultValues: props.defaultValues,
  })
  const handleSubmit = form.handleSubmit((values) => props.onSubmit(values, form))

  return (
    <form onSubmit={(event) => void handleSubmit(event)} className="grid gap-4" noValidate>
      <FormErrorBanner message={props.errorMessage} />
      <IdentificationSection form={form} />
      <AddressSection form={form} />
      <DocumentsSection form={form} />
      <OwnershipSection form={form} showActive={props.isEdit} />
      <AcquisitionValuesSection form={form} />
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={props.onCancel}>
          Cancelar
        </Button>
        <Button type="submit" disabled={props.isPending}>
          {props.submitLabel}
        </Button>
      </div>
    </form>
  )
}
