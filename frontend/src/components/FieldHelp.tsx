// Botão "?" ao lado de um campo: abre um resumo da ajuda daquele campo, com link para o
// detalhe completo na página /ajuda. O conteúdo vem de `features/help/content.ts` — um
// texto só, usado aqui e na página.

import { CircleHelp } from 'lucide-react'
import { Link } from 'react-router'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import type { FieldHelp as FieldHelpContent } from '@/features/help/content'

function OptionList({ options }: { options: FieldHelpContent['options'] }) {
  if (!options) return null
  return (
    <dl className="grid gap-1.5">
      {options.map((option) => (
        <div key={option.value}>
          <dt className="font-medium text-foreground">{option.label}</dt>
          <dd className="text-muted-foreground">{option.effect}</dd>
        </div>
      ))}
    </dl>
  )
}

function ConstraintList({ constraints }: { constraints?: string[] }) {
  if (!constraints || constraints.length === 0) return null
  return (
    <ul className="list-disc pl-4 text-muted-foreground">
      {constraints.map((constraint) => (
        <li key={constraint}>{constraint}</li>
      ))}
    </ul>
  )
}

/** Corpo da ajuda de um campo: usado tanto no popover quanto na página /ajuda. */
export function FieldHelpBody({ content }: { content: FieldHelpContent }) {
  return (
    <div className="grid gap-2">
      <p>{content.description}</p>
      {content.format && (
        <p>
          <span className="font-medium text-foreground">Formato: </span>
          {content.format}
        </p>
      )}
      {content.examples && content.examples.length > 0 && (
        <p>
          <span className="font-medium text-foreground">Exemplos: </span>
          {content.examples.join(' · ')}
        </p>
      )}
      <ConstraintList constraints={content.constraints} />
      <OptionList options={content.options} />
    </div>
  )
}

export function FieldHelp({ content }: { content: FieldHelpContent }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          aria-label={`Ajuda sobre ${content.label}`}
          className="inline-flex size-4 shrink-0 items-center justify-center rounded-full text-muted-foreground outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/50"
        >
          <CircleHelp className="size-4" />
        </button>
      </PopoverTrigger>
      <PopoverContent>
        <div className="grid gap-3 text-sm">
          <p className="font-heading font-medium text-foreground">{content.label}</p>
          <FieldHelpBody content={content} />
          <Link
            to={`/ajuda#${content.id}`}
            className="text-xs font-medium text-primary underline underline-offset-3"
          >
            Ver mais na Ajuda →
          </Link>
        </div>
      </PopoverContent>
    </Popover>
  )
}
