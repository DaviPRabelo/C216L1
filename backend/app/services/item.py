from app.errors import DadosInvalidos, ItemNaoEncontrado
from app.repository import RepositorioDeItens
from app.schemas.item import Item

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


def criar_item(repo: RepositorioDeItens, nome: str, preco: float) -> Item:
    nome = _validar(nome, preco)
    return repo.adicionar(nome, preco)


def obter_item(repo: RepositorioDeItens, item_id: int) -> Item:
    item = repo.buscar(item_id)
    if item is None:
        raise ItemNaoEncontrado(item_id)
    return item


def listar_itens(repo: RepositorioDeItens, nome_contem: str | None = None) -> list[Item]:
    itens = repo.listar()
    if nome_contem:
        termo = nome_contem.lower()
        itens = [item for item in itens if termo in item.nome.lower()]
    return itens


def substituir_item(repo: RepositorioDeItens, item_id: int, nome: str, preco: float) -> Item:
    obter_item(repo, item_id)
    nome = _validar(nome, preco)
    return repo.salvar(Item(id=item_id, nome=nome, preco=preco))


def atualizar_item(
    repo: RepositorioDeItens,
    item_id: int,
    nome: str | None = None,
    preco: float | None = None,
) -> Item:
    atual = obter_item(repo, item_id)
    novo_nome = atual.nome if nome is None else nome
    novo_preco = atual.preco if preco is None else preco
    novo_nome = _validar(novo_nome, novo_preco)
    return repo.salvar(Item(id=item_id, nome=novo_nome, preco=novo_preco))


def remover_item(repo: RepositorioDeItens, item_id: int) -> None:
    if not repo.remover(item_id):
        raise ItemNaoEncontrado(item_id)
