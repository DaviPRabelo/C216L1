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


class StatusInventario(str, Enum):
    """Situação de uma contagem de inventário."""

    ABERTO = "ABERTO"
    FECHADO = "FECHADO"


class PapelUsuario(str, Enum):
    """Nível do operador na hierarquia do almoxarifado."""

    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    EMPREGADO = "EMPREGADO"


class CategoriaProduto(str, Enum):
    """Categorias previstas para os itens do almoxarifado."""

    FERRAMENTAS = "Ferramentas"
    FIXADORES = "Fixadores"
    EPI = "EPI"
    ELETRICA = "Elétrica"
    HIDRAULICA = "Hidráulica"
    LIMPEZA = "Limpeza"
    PAPELARIA = "Papelaria"
    CONSTRUCAO = "Construção"
    OUTROS = "Outros"
