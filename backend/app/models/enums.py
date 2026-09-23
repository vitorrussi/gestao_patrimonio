"""Enums do domínio. Os valores seguem exatamente o ESCOPO_IMOVEIS.md."""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Enum


class PropertyType(StrEnum):
    CASA = "casa"
    CASA_CONDOMINIO = "casa_condominio"
    APARTAMENTO = "apartamento"
    TERRENO = "terreno"
    TERRENO_CONDOMINIO = "terreno_condominio"
    SALA_COMERCIAL = "sala_comercial"
    LOJA = "loja"
    GALPAO = "galpao"
    PREDIO = "predio"
    CHACARA_SITIO = "chacara_sitio"
    FAZENDA = "fazenda"
    VAGA_GARAGEM = "vaga_garagem"
    BOX = "box"
    OUTRO = "outro"


class PropertyUsage(StrEnum):
    MORADIA_PROPRIA = "moradia_propria"
    ALUGADO = "alugado"
    VAZIO = "vazio"
    COMERCIAL_PROPRIO = "comercial_proprio"
    EM_CONSTRUCAO = "em_construcao"


class AcquisitionMethod(StrEnum):
    COMPRA = "compra"
    HERANCA = "heranca"
    DOACAO = "doacao"
    CONSTRUCAO = "construcao"
    OUTRO = "outro"


class ValuationSource(StrEnum):
    ESTIMATIVA_PROPRIA = "estimativa_propria"
    CORRETOR = "corretor"
    LAUDO = "laudo"
    ANUNCIO_SIMILAR = "anuncio_similar"
    OUTRO = "outro"


class AmortizationSystem(StrEnum):
    SAC = "sac"
    PRICE = "price"
    OUTRO = "outro"


class InterestIndex(StrEnum):
    TR = "tr"
    IPCA = "ipca"
    PREFIXADO = "prefixado"
    OUTRO = "outro"


class ExpenseType(StrEnum):
    IPTU = "iptu"
    CONDOMINIO = "condominio"
    COTA_EXTRA = "cota_extra"
    SEGURO = "seguro"
    AGUA = "agua"
    LUZ = "luz"
    GAS = "gas"
    INTERNET = "internet"
    TAXA_LIXO = "taxa_lixo"
    ITR = "itr"
    LAUDEMIO_FORO = "laudemio_foro"
    MANUTENCAO = "manutencao"
    OUTRO = "outro"


class Frequency(StrEnum):
    MENSAL = "mensal"
    BIMESTRAL = "bimestral"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"
    UNICA = "unica"


class DueStatus(StrEnum):
    """Status calculado de um vencimento (não é gravado no banco)."""

    PAGO = "pago"
    A_PAGAR = "a_pagar"
    ATRASADO = "atrasado"


def enum_type(enum_cls: type[StrEnum], name: str) -> Enum:
    """Enum gravado como texto com CHECK dos valores (sem tipo nativo do banco)."""
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )
