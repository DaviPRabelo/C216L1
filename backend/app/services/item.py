from app.errors import DadosInvalidos, ItemNaoEncontrado, NomeJaExiste
from app.models.item import ItemORM
from app.repositories.item import RepositorioDeItens

NOME_MAXIMO = 60
DESCRICAO_MAXIMA = 200
PRECO_MAXIMO = 1_000_000
QUANTIDADE_MAXIMA = 9999

CATEGORIAS = ("Eletrônicos", "Periféricos", "Móveis", "Papelaria", "Outros")


def _validar(nome: str, descricao: str, categoria: str, quantidade: int, preco: float) -> tuple:
    nome = (nome or "").strip()
    descricao = (descricao or "").strip()

    if not nome:
        raise DadosInvalidos("O nome é obrigatório")
    if len(nome) > NOME_MAXIMO:
        raise DadosInvalidos(f"O nome deve ter até {NOME_MAXIMO} caracteres")
    if len(descricao) > DESCRICAO_MAXIMA:
        raise DadosInvalidos(f"A descrição deve ter até {DESCRICAO_MAXIMA} caracteres")
    if categoria not in CATEGORIAS:
        raise DadosInvalidos("Categoria inválida")
    if quantidade < 1:
        raise DadosInvalidos("A quantidade deve ser pelo menos 1")
    if quantidade > QUANTIDADE_MAXIMA:
        raise DadosInvalidos(f"A quantidade não pode passar de {QUANTIDADE_MAXIMA}")
    if preco < 0:
        raise DadosInvalidos("O preço não pode ser negativo")
    if preco > PRECO_MAXIMO:
        raise DadosInvalidos(f"O preço não pode passar de {PRECO_MAXIMO}")

    return nome, descricao


def _garantir_nome_livre(repo: RepositorioDeItens, nome: str, item_id: int | None = None) -> None:
    existente = repo.buscar_por_nome(nome)
    if existente is not None and existente.id != item_id:
        raise NomeJaExiste(nome)


def criar_item(
    repo: RepositorioDeItens,
    nome: str,
    descricao: str = "",
    categoria: str = "",
    quantidade: int = 1,
    preco: float = 0.0,
) -> ItemORM:
    nome, descricao = _validar(nome, descricao, categoria, quantidade, preco)
    _garantir_nome_livre(repo, nome)
    return repo.adicionar(nome, descricao, categoria, quantidade, preco)


def obter_item(repo: RepositorioDeItens, item_id: int) -> ItemORM:
    item = repo.buscar(item_id)
    if item is None:
        raise ItemNaoEncontrado(item_id)
    return item


def listar_itens(repo: RepositorioDeItens, nome_contem: str | None = None) -> list[ItemORM]:
    return repo.listar(nome_contem)


def substituir_item(
    repo: RepositorioDeItens,
    item_id: int,
    nome: str,
    descricao: str,
    categoria: str,
    quantidade: int,
    preco: float,
) -> ItemORM:
    item = obter_item(repo, item_id)
    nome, descricao = _validar(nome, descricao, categoria, quantidade, preco)
    _garantir_nome_livre(repo, nome, item_id)
    return repo.atualizar(item, nome, descricao, categoria, quantidade, preco)


def atualizar_item(
    repo: RepositorioDeItens,
    item_id: int,
    nome: str | None = None,
    descricao: str | None = None,
    categoria: str | None = None,
    quantidade: int | None = None,
    preco: float | None = None,
) -> ItemORM:
    atual = obter_item(repo, item_id)
    novo_nome = atual.nome if nome is None else nome
    nova_descricao = atual.descricao if descricao is None else descricao
    nova_categoria = atual.categoria if categoria is None else categoria
    nova_quantidade = atual.quantidade if quantidade is None else quantidade
    novo_preco = atual.preco if preco is None else preco

    novo_nome, nova_descricao = _validar(
        novo_nome, nova_descricao, nova_categoria, nova_quantidade, novo_preco
    )
    _garantir_nome_livre(repo, novo_nome, item_id)
    return repo.atualizar(
        atual, novo_nome, nova_descricao, nova_categoria, nova_quantidade, novo_preco
    )


def remover_item(repo: RepositorioDeItens, item_id: int) -> None:
    if not repo.remover(item_id):
        raise ItemNaoEncontrado(item_id)
