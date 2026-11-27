from datetime import date

from app.errors import (
    ContagemIncompleta,
    DadosInvalidos,
    InventarioJaFechado,
    InventarioNaoEncontrado,
    ItemDeInventarioNaoEncontrado,
    JaExisteInventarioAberto,
)
from app.models.inventario import InventarioORM
from app.repositories.inventario import RepositorioDeInventarios
from app.repositories.produto import RepositorioDeProdutos

RESPONSAVEL_MAXIMO = 100
QUANTIDADE_MAXIMA = 999_999


def abrir_inventario(
    repo: RepositorioDeInventarios,
    repo_produtos: RepositorioDeProdutos,
    almoxarifado_id: int,
    responsavel: str,
    data_da_contagem: date | None = None,
) -> InventarioORM:
    responsavel = (responsavel or "").strip()
    if not responsavel:
        raise DadosInvalidos("O responsável pela contagem é obrigatório")
    if len(responsavel) > RESPONSAVEL_MAXIMO:
        raise DadosInvalidos(f"O responsável deve ter até {RESPONSAVEL_MAXIMO} caracteres")

    aberto = repo.buscar_aberto(almoxarifado_id)
    if aberto is not None:
        raise JaExisteInventarioAberto(aberto.id)

    produtos = repo_produtos.listar(almoxarifado_id)
    if not produtos:
        raise DadosInvalidos("Não há produtos cadastrados neste almoxarifado para contar")

    return repo.abrir(almoxarifado_id, data_da_contagem or date.today(), responsavel, produtos)


def obter_inventario(repo: RepositorioDeInventarios, inventario_id: int) -> InventarioORM:
    inventario = repo.buscar(inventario_id)
    if inventario is None:
        raise InventarioNaoEncontrado(inventario_id)
    return inventario


def listar_inventarios(
    repo: RepositorioDeInventarios, almoxarifado_id: int | None = None
) -> list[InventarioORM]:
    return repo.listar(almoxarifado_id)


def contar_item(
    repo: RepositorioDeInventarios, inventario_id: int, produto_id: int, quantidade: int
) -> InventarioORM:
    inventario = obter_inventario(repo, inventario_id)
    if not inventario.aberto:
        raise InventarioJaFechado(inventario_id)

    if quantidade < 0:
        raise DadosInvalidos("A quantidade contada não pode ser negativa")
    if quantidade > QUANTIDADE_MAXIMA:
        raise DadosInvalidos(f"A quantidade não pode passar de {QUANTIDADE_MAXIMA}")

    item = next((i for i in inventario.itens if i.produto_id == produto_id), None)
    if item is None:
        raise ItemDeInventarioNaoEncontrado(produto_id)

    repo.registrar_contagem(item, quantidade)
    return obter_inventario(repo, inventario_id)


def fechar_inventario(repo: RepositorioDeInventarios, inventario_id: int) -> InventarioORM:
    inventario = obter_inventario(repo, inventario_id)
    if not inventario.aberto:
        raise InventarioJaFechado(inventario_id)

    faltando = len(inventario.itens) - inventario.itens_contados
    if faltando > 0:
        raise ContagemIncompleta(faltando)

    return repo.fechar(inventario)
