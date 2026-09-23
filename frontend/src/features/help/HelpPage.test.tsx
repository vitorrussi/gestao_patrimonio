// Smoke test: a página renderiza a seção de Financiamento, com um elemento por campo
// cujo id bate com a âncora que o "?" dos formulários usa, e os exemplos de uso.

import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { afterEach, describe, expect, it } from 'vitest'
import { HelpPage } from './HelpPage'
import { financingHelp, helpSections } from './content'

afterEach(() => cleanup())

describe('HelpPage', () => {
  it('renderiza a seção de financiamento com um card por campo', () => {
    render(
      <MemoryRouter>
        <HelpPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Financiamento' })).toBeTruthy()
    for (const field of Object.values(financingHelp)) {
      const title = screen.getByText(field.label)
      expect(document.getElementById(field.id)?.contains(title)).toBe(true)
    }
  })

  it('renderiza os passos de cada exemplo de uso', () => {
    render(
      <MemoryRouter>
        <HelpPage />
      </MemoryRouter>,
    )

    const [example] = helpSections[0].usageExamples
    expect(screen.getByText(example.title)).toBeTruthy()
    for (const step of example.steps) {
      expect(screen.getAllByText(step).length).toBeGreaterThan(0)
    }
  })
})
