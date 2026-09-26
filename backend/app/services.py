from app.errors import DadosInvalidos, ItemNaoEncontrado
from app.models import Item
from app.repository import RepositorioDeItens

PRECO_MAXIMO = 1_000_000


def criar_item(repo: RepositorioDeItens, nome: str, preco: float) -> Item:
    nome = nome.strip()
    if not nome:
        raise DadosInvalidos("O nome do item não pode ser vazio")
    if preco < 0:
        raise DadosInvalidos("O preço não pode ser negativo")
    if preco > PRECO_MAXIMO:
        raise DadosInvalidos(f"O preço não pode passar de {PRECO_MAXIMO}")
    return repo.adicionar(nome, preco)


def obter_item(repo: RepositorioDeItens, item_id: int) -> Item:
    item = repo.buscar(item_id)
    if item is None:
        raise ItemNaoEncontrado(item_id)
    return item


def remover_item(repo: RepositorioDeItens, item_id: int) -> None:
    if not repo.remover(item_id):
        raise ItemNaoEncontrado(item_id)
