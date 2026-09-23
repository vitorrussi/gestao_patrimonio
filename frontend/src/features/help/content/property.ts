import type { FieldHelp, HelpSection } from '../types'

/** Chave = `name` do campo no formulário de imóvel (`PropertyFormValues`). */
export const propertyHelp = {
  nickname: {
    id: 'property-nickname',
    label: 'Apelido',
    description: 'Como você quer chamar o imóvel nas telas do app.',
    format: 'Texto livre, até 100 caracteres.',
    examples: ['Apto Centro', 'Terreno Pirabeiraba'],
    constraints: ['Obrigatório.'],
  },
  property_type: {
    id: 'property-property_type',
    label: 'Tipo',
    description:
      'O que é o imóvel (casa, apartamento, terreno etc.). Só usado para agrupar a contagem por tipo no painel geral — não muda nenhum valor calculado.',
    format:
      'Lista fixa: casa, casa em condomínio, apartamento, terreno, terreno em condomínio, sala comercial, loja, galpão, prédio, chácara/sítio, fazenda, vaga de garagem, box ou outro.',
    constraints: ['Obrigatório.'],
  },
  usage: {
    id: 'property-usage',
    label: 'Uso',
    description:
      'Para que o imóvel serve hoje (moradia própria, alugado, vazio, comercial próprio ou em construção). Só informativo por enquanto — contratos de locação e receita de aluguel entram numa fase futura do app.',
    constraints: ['Obrigatório.'],
  },
  street: {
    id: 'property-street',
    label: 'Logradouro',
    description: 'Rua/avenida do endereço. Só para referência, não entra em cálculo.',
    format: 'Texto livre, até 200 caracteres.',
    constraints: ['Opcional.'],
  },
  number: {
    id: 'property-number',
    label: 'Número',
    description: 'Número do endereço.',
    format: 'Texto livre, até 20 caracteres (aceita "s/n").',
    constraints: ['Opcional.'],
  },
  complement: {
    id: 'property-complement',
    label: 'Complemento',
    description: 'Bloco, apartamento, sala etc.',
    format: 'Texto livre, até 100 caracteres.',
    constraints: ['Opcional.'],
  },
  neighborhood: {
    id: 'property-neighborhood',
    label: 'Bairro',
    format: 'Texto livre, até 100 caracteres.',
    description: 'Bairro do endereço.',
    constraints: ['Opcional.'],
  },
  city: {
    id: 'property-city',
    label: 'Cidade',
    description: 'Cidade do endereço.',
    format: 'Texto livre, até 100 caracteres.',
    constraints: ['Opcional.'],
  },
  state: {
    id: 'property-state',
    label: 'UF',
    description: 'Estado do endereço, na sigla de 2 letras.',
    format: '2 letras.',
    examples: ['SC', 'SP'],
    constraints: ['Opcional.'],
  },
  zip_code: {
    id: 'property-zip_code',
    label: 'CEP',
    description: 'CEP do endereço.',
    format: '8 dígitos, com ou sem hífen.',
    examples: ['89200-000', '89200000'],
    constraints: ['Opcional.'],
  },
  registration_number: {
    id: 'property-registration_number',
    label: 'Matrícula',
    description: 'Número da matrícula do imóvel no cartório de registro de imóveis.',
    format: 'Texto livre, até 50 caracteres.',
    constraints: ['Opcional.'],
  },
  registry_office: {
    id: 'property-registry_office',
    label: 'Cartório de registro',
    description: 'Qual cartório tem a matrícula.',
    format: 'Texto livre, até 150 caracteres.',
    examples: ['1º Registro de Imóveis de Joinville'],
    constraints: ['Opcional.'],
  },
  municipal_registration: {
    id: 'property-municipal_registration',
    label: 'Inscrição imobiliária (IPTU)',
    description: 'Número de cadastro do imóvel na prefeitura, usado no carnê do IPTU.',
    format: 'Texto livre, até 50 caracteres.',
    constraints: ['Opcional.'],
  },
  ownership_percentage: {
    id: 'property-ownership_percentage',
    label: 'Participação (%)',
    description:
      'Quanto do imóvel é seu, quando ele tem coproprietários. Multiplica o valor de mercado ao calcular o patrimônio bruto e líquido — mas não reduz a dívida, que aparece inteira independente da sua participação.',
    format: 'Número com vírgula decimal, até 4 casas.',
    examples: ['100 (imóvel só seu)', '50 (metade, com coproprietário)'],
    constraints: ['Obrigatório.', 'De 0 a 100. Padrão: 100.'],
  },
  acquisition_date: {
    id: 'property-acquisition_date',
    label: 'Data de aquisição',
    description: 'Quando você passou a ser dono do imóvel. Só para referência (e IR futuro).',
    format: 'Data (dd/mm/aaaa).',
    constraints: ['Opcional.'],
  },
  acquisition_method: {
    id: 'property-acquisition_method',
    label: 'Forma de aquisição',
    description:
      'Como você adquiriu o imóvel. Só informativo hoje (útil para a visão de Imposto de Renda numa fase futura); não muda nenhum cálculo atual.',
    options: [
      {
        value: 'compra',
        label: 'Compra',
        effect: 'Você pagou um valor por um imóvel já existente (pronto ou terreno).',
      },
      {
        value: 'heranca',
        label: 'Herança',
        effect: 'Recebido em inventário, normalmente sem valor de compra.',
      },
      { value: 'doacao', label: 'Doação', effect: 'Recebido por doação em vida.' },
      {
        value: 'construcao',
        label: 'Construção',
        effect:
          'Você não comprou um imóvel pronto — construiu, seja em terreno que já era seu ou recém-adquirido. O custo da obra entra como benfeitoria (Versão 2), não como "Valor de compra".',
      },
      {
        value: 'outro',
        label: 'Outro',
        effect: 'Qualquer caso que não se encaixe nos anteriores.',
      },
    ],
  },
  purchase_price: {
    id: 'property-purchase_price',
    label: 'Valor de compra (R$)',
    description:
      'O que você pagou pelo imóvel. Soma com ITBI e escritura/registro para formar o "Valor total de aquisição" mostrado na ficha do imóvel — esse valor não muda com o mercado, só com benfeitorias (Versão 2).',
    format: 'Reais com vírgula decimal.',
    examples: ['300.000,00'],
    constraints: ['Opcional.'],
  },
  itbi: {
    id: 'property-itbi',
    label: 'ITBI (R$)',
    description: 'Imposto de transmissão pago na compra. Soma no valor total de aquisição.',
    format: 'Reais com vírgula decimal.',
    examples: ['9.000,00'],
    constraints: ['Opcional.'],
  },
  deed_registration: {
    id: 'property-deed_registration',
    label: 'Escritura e registro (R$)',
    description: 'Custos de escritura e registro em cartório. Soma no valor total de aquisição.',
    format: 'Reais com vírgula decimal.',
    examples: ['2.500,00'],
    constraints: ['Opcional.'],
  },
  is_active: {
    id: 'property-is_active',
    label: 'Imóvel ativo',
    description:
      'Desmarque quando o imóvel for vendido. Ele some do painel geral e dos compromissos do mês, mas o histórico (avaliações, financiamentos, pagamentos) continua existindo — só editando de novo.',
    options: [
      {
        value: 'true',
        label: 'Marcado (ativo)',
        effect: 'Entra no patrimônio bruto/líquido do painel e continua gerando compromissos.',
      },
      {
        value: 'false',
        label: 'Desmarcado (vendido/inativo)',
        effect: 'Sai dos totais do painel e para de gerar vencimentos novos.',
      },
    ],
  },
} as const satisfies Record<string, FieldHelp>

export const propertySection: HelpSection = {
  id: 'imovel',
  title: 'Imóvel',
  intro:
    'O cadastro do imóvel é só "o que ele é" — identificação, endereço, documentação e como foi adquirido. Valores de mercado, financiamentos, despesas e pagamentos ficam em registros separados, ligados a este imóvel.',
  fields: Object.values(propertyHelp),
  usageExamples: [
    {
      title: 'Cadastrar um imóvel comprado',
      steps: [
        'No menu, vá em "Imóveis" e clique em "Novo imóvel".',
        'Preencha apelido, tipo e uso.',
        'Preencha endereço e documentação (matrícula, cartório, inscrição do IPTU) se já tiver em mãos — dá para completar depois.',
        'Em "Forma de aquisição", escolha "Compra" e preencha valor de compra, ITBI e escritura/registro.',
        'Salve. Cadastre a primeira avaliação de mercado e, se houver, o financiamento.',
      ],
    },
    {
      title: 'Marcar um imóvel como vendido',
      steps: [
        'Abra a ficha do imóvel e clique em "Editar".',
        'Desmarque "Imóvel ativo".',
        'Salve. O imóvel sai do painel geral e dos compromissos do mês, mas o histórico continua acessível na ficha dele (em "Vendidos / inativos", na lista de imóveis).',
      ],
    },
  ],
}
