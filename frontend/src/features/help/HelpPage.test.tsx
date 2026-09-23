// Smoke test: a página renderiza cada seção (imóvel, avaliação, financiamento, despesa)
// com um elemento por campo cujo id bate com a âncora que o "?" dos formulários usa, e os
// passos de cada exemplo de uso.

import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { afterEach, describe, expect, it } from 'vitest'
import { HelpPage } from './HelpPage'
import { helpSections } from './content'

afterEach(() => cleanup())

describe('HelpPage', () => {
  it('renderiza um card por campo, na âncora certa, em cada seção', () => {
    render(
      <MemoryRouter>
        <HelpPage />
      </MemoryRouter>,
    )

    for (const section of helpSections) {
      expect(screen.getByRole('heading', { name: section.title })).toBeTruthy()
      for (const field of section.fields) {
        const card = document.getElementById(field.id)
        expect(card, `card #${field.id} (${section.title})`).toBeTruthy()
        expect(card?.textContent).toContain(field.label)
      }
    }
  })

  it('renderiza os passos de cada exemplo de uso', () => {
    render(
      <MemoryRouter>
        <HelpPage />
      </MemoryRouter>,
    )

    for (const section of helpSections) {
      for (const example of section.usageExamples) {
        expect(screen.getByText(example.title)).toBeTruthy()
        for (const step of example.steps) {
          expect(screen.getAllByText(step).length).toBeGreaterThan(0)
        }
      }
    }
  })
})
