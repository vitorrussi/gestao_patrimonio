// Página /ajuda: descrição completa de cada campo dos formulários, organizada por
// entidade, com exemplos de uso passo a passo. O "?" dos formulários linka para cá
// (âncora = FieldHelp.id). Conteúdo vem todo de `features/help/content.ts`.

import { useEffect } from 'react'
import { useLocation } from 'react-router'
import { FieldHelpBody } from '@/components/FieldHelp'
import { PageHeader } from '@/components/display'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { FieldHelp, HelpSection, UsageExample } from '@/features/help/content'
import { helpSections } from '@/features/help/content'

/** Rola até o campo linkado pelo "?" (ex.: vindo de /ajuda#financing-lender). */
function useScrollToHash() {
  const { hash } = useLocation()
  useEffect(() => {
    if (!hash) return
    document.getElementById(hash.slice(1))?.scrollIntoView({ block: 'start' })
  }, [hash])
}

function FieldCard({ field }: { field: FieldHelp }) {
  return (
    <Card id={field.id} className="scroll-mt-20">
      <CardHeader>
        <CardTitle className="text-base">{field.label}</CardTitle>
      </CardHeader>
      <CardContent>
        <FieldHelpBody content={field} />
      </CardContent>
    </Card>
  )
}

function UsageExampleCard({ example }: { example: UsageExample }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{example.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="grid list-decimal gap-1 pl-4 text-sm text-muted-foreground">
          {example.steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </CardContent>
    </Card>
  )
}

function Section({ section }: { section: HelpSection }) {
  return (
    <section className="grid gap-4">
      <div className="scroll-mt-20" id={section.id}>
        <h2 className="font-heading text-xl font-semibold">{section.title}</h2>
        <p className="text-sm text-muted-foreground">{section.intro}</p>
      </div>
      <div className="grid gap-3">
        <h3 className="text-sm font-medium text-muted-foreground">Campos</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {section.fields.map((field) => (
            <FieldCard key={field.id} field={field} />
          ))}
        </div>
      </div>
      <div className="grid gap-3">
        <h3 className="text-sm font-medium text-muted-foreground">Exemplos de uso</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {section.usageExamples.map((example) => (
            <UsageExampleCard key={example.title} example={example} />
          ))}
        </div>
      </div>
    </section>
  )
}

export function HelpPage() {
  useScrollToHash()
  return (
    <div className="grid gap-8">
      <PageHeader
        title="Ajuda"
        description="O que cada campo significa, como preencher e como afeta os cálculos. Também dá para chegar aqui pelo “?” ao lado de cada campo."
      />
      {helpSections.map((section) => (
        <Section key={section.id} section={section} />
      ))}
    </div>
  )
}
