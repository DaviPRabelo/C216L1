from app.errors import (
    CodigoJaExiste,
    DadosInvalidos,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
)
from app.models.enums import UnidadeMedida
from app.models.produto import ProdutoORM
from app.repositories.produto import RepositorioDeProdutos

CODIGO_MAXIMO = 20
NOME_MAXIMO = 100
DESCRICAO_MAXIMA = 200
CATEGORIA_MAXIMA = 50
ESTOQUE_MINIMO_MAXIMO = 999_999


def _normalizar_e_validar(
    codigo: str, nome: str, descricao: str, categoria: str, estoque_minimo: int
) -> tuple[str, str, str, str]:
    codigo = (codigo or "").strip().upper()
    nome = (nome or "").strip()
    descricao = (descricao or "").strip()
    categoria = (categoria or "").strip()

    if not codigo:
        raise DadosInvalidos("O código é obrigatório")
    if len(codigo) > CODIGO_MAXIMO:
        raise DadosInvalidos(f"O código deve ter até {CODIGO_MAXIMO} caracteres")
    if not nome:
        raise DadosInvalidos("O nome é obrigatório")
    if len(nome) > NOME_MAXIMO:
        raise DadosInvalidos(f"O nome deve ter até {NOME_MAXIMO} caracteres")
    if len(descricao) > DESCRICAO_MAXIMA:
        raise DadosInvalidos(f"A descrição deve ter até {DESCRICAO_MAXIMA} caracteres")
    if not categoria:
        raise DadosInvalidos("A categoria é obrigatória")
    if len(categoria) > CATEGORIA_MAXIMA:
        raise DadosInvalidos(f"A categoria deve ter até {CATEGORIA_MAXIMA} caracteres")
    if estoque_minimo < 0:
        raise DadosInvalidos("O estoque mínimo não pode ser negativo")
    if estoque_minimo > ESTOQUE_MINIMO_MAXIMO:
        raise DadosInvalidos(f"O estoque mínimo não pode passar de {ESTOQUE_MINIMO_MAXIMO}")

    return codigo, nome, descricao, categoria


def _garantir_codigo_livre(
    repo: RepositorioDeProdutos, codigo: str, produto_id: int | None = None
) -> None:
    existente = repo.buscar_por_codigo(codigo)
    if existente is not None and existente.id != produto_id:
        raise CodigoJaExiste(codigo)


def criar_produto(
    repo: RepositorioDeProdutos,
    codigo: str,
    nome: str,
    categoria: str,
    unidade: UnidadeMedida,
    descricao: str = "",
    estoque_minimo: int = 0,
) -> ProdutoORM:
    codigo, nome, descricao, categoria = _normalizar_e_validar(
        codigo, nome, descricao, categoria, estoque_minimo
    )
    _garantir_codigo_livre(repo, codigo)

    return repo.adicionar(
        codigo=codigo,
        nome=nome,
        descricao=descricao,
        categoria=categoria,
        unidade=unidade,
        estoque_minimo=estoque_minimo,
        saldo=0,
    )


def obter_produto(repo: RepositorioDeProdutos, produto_id: int) -> ProdutoORM:
    produto = repo.buscar(produto_id)
    if produto is None:
        raise ProdutoNaoEncontrado(produto_id)
    return produto


def listar_produtos(
    repo: RepositorioDeProdutos,
    categoria: str | None = None,
    apenas_abaixo_do_minimo: bool = False,
) -> list[ProdutoORM]:
    return repo.listar(categoria, apenas_abaixo_do_minimo)


def listar_categorias(repo: RepositorioDeProdutos) -> list[str]:
    return repo.categorias()


def atualizar_produto(
    repo: RepositorioDeProdutos,
    produto_id: int,
    codigo: str | None = None,
    nome: str | None = None,
    descricao: str | None = None,
    categoria: str | None = None,
    unidade: UnidadeMedida | None = None,
    estoque_minimo: int | None = None,
) -> ProdutoORM:
    produto = obter_produto(repo, produto_id)

    novo_codigo = produto.codigo if codigo is None else codigo
    novo_nome = produto.nome if nome is None else nome
    nova_descricao = produto.descricao if descricao is None else descricao
    nova_categoria = produto.categoria if categoria is None else categoria
    nova_unidade = produto.unidade if unidade is None else unidade
    novo_minimo = produto.estoque_minimo if estoque_minimo is None else estoque_minimo

    novo_codigo, novo_nome, nova_descricao, nova_categoria = _normalizar_e_validar(
        novo_codigo, novo_nome, nova_descricao, nova_categoria, novo_minimo
    )
    _garantir_codigo_livre(repo, novo_codigo, produto_id)

    return repo.atualizar(
        produto,
        codigo=novo_codigo,
        nome=novo_nome,
        descricao=nova_descricao,
        categoria=nova_categoria,
        unidade=nova_unidade,
        estoque_minimo=novo_minimo,
    )


def remover_produto(repo: RepositorioDeProdutos, produto_id: int) -> None:
    produto = obter_produto(repo, produto_id)
    if repo.tem_movimentacoes(produto):
        raise ProdutoComMovimentacoes(produto_id)
    repo.remover(produto)
