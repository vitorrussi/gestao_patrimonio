import { z } from 'zod'
import type { PropertyDetail, PropertyFields } from '@/api/types'
import {
  emptyToNull,
  enumText,
  optionalDate,
  optionalEnumText,
  optionalMoney,
  optionalText,
  percentText,
  requiredText,
  toOptionalCents,
  toPercent,
} from '@/lib/formFields'
import {
  ACQUISITION_METHOD_LABELS,
  type AcquisitionMethod,
  PROPERTY_TYPE_LABELS,
  PROPERTY_USAGE_LABELS,
  type PropertyType,
  type PropertyUsage,
} from '@/lib/labels'
import { centsToInput } from '@/lib/money'
import { apiPercentToInput } from '@/lib/percent'

export const propertySchema = z.object({
  nickname: requiredText(100),
  property_type: enumText(PROPERTY_TYPE_LABELS),
  usage: enumText(PROPERTY_USAGE_LABELS),
  street: optionalText(200),
  number: optionalText(20),
  complement: optionalText(100),
  neighborhood: optionalText(100),
  city: optionalText(100),
  state: z
    .string()
    .trim()
    .refine((value) => value === '' || /^[A-Za-z]{2}$/.test(value), 'UF com 2 letras. Ex.: SC'),
  zip_code: z
    .string()
    .trim()
    .refine((value) => value === '' || /^\d{5}-?\d{3}$/.test(value), 'CEP no formato 00000-000.'),
  registration_number: optionalText(50),
  registry_office: optionalText(150),
  municipal_registration: optionalText(50),
  ownership_percentage: percentText(100),
  acquisition_date: optionalDate,
  acquisition_method: optionalEnumText(ACQUISITION_METHOD_LABELS),
  purchase_price: optionalMoney,
  itbi: optionalMoney,
  deed_registration: optionalMoney,
  is_active: z.boolean(),
})

export type PropertyFormValues = z.infer<typeof propertySchema>

export const EMPTY_PROPERTY: PropertyFormValues = {
  nickname: '',
  property_type: '',
  usage: '',
  street: '',
  number: '',
  complement: '',
  neighborhood: '',
  city: '',
  state: '',
  zip_code: '',
  registration_number: '',
  registry_office: '',
  municipal_registration: '',
  ownership_percentage: '100',
  acquisition_date: '',
  acquisition_method: '',
  purchase_price: '',
  itbi: '',
  deed_registration: '',
  is_active: true,
}

const OPTIONAL_TEXT_FIELDS = [
  'street',
  'number',
  'complement',
  'neighborhood',
  'city',
  'state',
  'zip_code',
  'registration_number',
  'registry_office',
  'municipal_registration',
  'acquisition_date',
  'acquisition_method',
] as const

export function propertyToForm(property: PropertyDetail): PropertyFormValues {
  const optionalTexts = Object.fromEntries(
    OPTIONAL_TEXT_FIELDS.map((field) => [field, property[field] ?? '']),
  ) as Pick<PropertyFormValues, (typeof OPTIONAL_TEXT_FIELDS)[number]>
  return {
    ...optionalTexts,
    nickname: property.nickname,
    property_type: property.property_type,
    usage: property.usage,
    ownership_percentage: apiPercentToInput(property.ownership_percentage),
    purchase_price: centsToInput(property.purchase_price_cents),
    itbi: centsToInput(property.itbi_cents),
    deed_registration: centsToInput(property.deed_registration_cents),
    is_active: property.is_active,
  }
}

export function formToProperty(values: PropertyFormValues): PropertyFields {
  return {
    nickname: values.nickname.trim(),
    property_type: values.property_type as PropertyType,
    usage: values.usage as PropertyUsage,
    street: emptyToNull(values.street),
    number: emptyToNull(values.number),
    complement: emptyToNull(values.complement),
    neighborhood: emptyToNull(values.neighborhood),
    city: emptyToNull(values.city),
    state: emptyToNull(values.state),
    zip_code: emptyToNull(values.zip_code),
    registration_number: emptyToNull(values.registration_number),
    registry_office: emptyToNull(values.registry_office),
    municipal_registration: emptyToNull(values.municipal_registration),
    ownership_percentage: toPercent(values.ownership_percentage, 100),
    acquisition_date: emptyToNull(values.acquisition_date),
    acquisition_method:
      (emptyToNull(values.acquisition_method) as AcquisitionMethod | null) ?? null,
    purchase_price_cents: toOptionalCents(values.purchase_price),
    itbi_cents: toOptionalCents(values.itbi),
    deed_registration_cents: toOptionalCents(values.deed_registration),
    is_active: values.is_active,
  }
}
