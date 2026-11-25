from enum import Enum


class UnidadeMedida(str, Enum):
    """Unidade em que o produto é controlado."""

    UNIDADE = "UN"
    CAIXA = "CX"
    QUILO = "KG"
    LITRO = "L"


class TipoMovimentacao(str, Enum):
    """Natureza da movimentação de estoque."""

    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
