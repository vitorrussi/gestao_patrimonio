// O "?" abre um resumo do campo (descrição, formato, exemplos, opções) e linka para o
// detalhe completo em /ajuda#<id>.

import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeAll, describe, expect, it } from 'vitest'
import { FieldHelp } from './FieldHelp'
import type { FieldHelp as FieldHelpContent } from '@/features/help/content'

beforeAll(() => {
  Element.prototype.hasPointerCapture = () => false
  Element.prototype.scrollIntoView = () => {}
})

afterEach(() => cleanup())

const content: FieldHelpContent = {
  id: 'financing-amortization_system',
  label: 'Sistema de amortização',
  description: 'Só informativo hoje.',
  options: [
    { value: 'sac', label: 'SAC', effect: 'Parcela cai mês a mês.' },
    { value: 'price', label: 'Price', effect: 'Parcela fixa.' },
  ],
}

function renderHelp() {
  render(
    <MemoryRouter>
      <FieldHelp content={content} />
    </MemoryRouter>,
  )
}

describe('FieldHelp', () => {
  it('mostra descrição e opções ao clicar no "?"', async () => {
    renderHelp()
    expect(screen.queryByText('Só informativo hoje.')).toBeNull()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajuda sobre Sistema de amortização' }),
    )

    expect(await screen.findByText('Só informativo hoje.')).toBeTruthy()
    expect(screen.getByText('SAC')).toBeTruthy()
    expect(screen.getByText('Parcela cai mês a mês.')).toBeTruthy()
  })

  it('linka para a âncora correspondente na página Ajuda', async () => {
    renderHelp()
    await userEvent.click(
      screen.getByRole('button', { name: 'Ajuda sobre Sistema de amortização' }),
    )

    const link = await screen.findByRole('link', { name: 'Ver mais na Ajuda →' })
    expect(link.getAttribute('href')).toBe('/ajuda#financing-amortization_system')
  })
})
