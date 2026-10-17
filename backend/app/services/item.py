from app.errors import DadosInvalidos, ItemNaoEncontrado
from app.models.item import ItemORM
from app.repositories.item import RepositorioDeItens

PRECO_MAXIMO = 1_000_000


def _validar(nome: str, preco: float) -> str:
    nome = nome.strip()
    if not nome:
        raise DadosInvalidos("O nome do item não pode ser vazio")
    if preco < 0:
        raise DadosInvalidos("O preço não pode ser negativo")
    if preco > PRECO_MAXIMO:
        raise DadosInvalidos(f"O preço não pode passar de {PRECO_MAXIMO}")
    return nome


def criar_item(repo: RepositorioDeItens, nome: str, preco: float) -> ItemORM:
    nome = _validar(nome, preco)
    return repo.adicionar(nome, preco)


def obter_item(repo: RepositorioDeItens, item_id: int) -> ItemORM:
    item = repo.buscar(item_id)
    if item is None:
        raise ItemNaoEncontrado(item_id)
    return item


def listar_itens(repo: RepositorioDeItens, nome_contem: str | None = None) -> list[ItemORM]:
    return repo.listar(nome_contem)


def substituir_item(
    repo: RepositorioDeItens, item_id: int, nome: str, preco: float
) -> ItemORM:
    item = obter_item(repo, item_id)
    nome = _validar(nome, preco)
    return repo.atualizar(item, nome, preco)


def atualizar_item(
    repo: RepositorioDeItens,
    item_id: int,
    nome: str | None = None,
    preco: float | None = None,
) -> ItemORM:
    atual = obter_item(repo, item_id)
    novo_nome = atual.nome if nome is None else nome
    novo_preco = atual.preco if preco is None else preco
    novo_nome = _validar(novo_nome, novo_preco)
    return repo.atualizar(atual, novo_nome, novo_preco)


def remover_item(repo: RepositorioDeItens, item_id: int) -> None:
    if not repo.remover(item_id):
        raise ItemNaoEncontrado(item_id)
