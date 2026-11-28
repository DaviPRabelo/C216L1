from app.errors import (
    CodigoJaExiste,
    DadosInvalidos,
    ProdutoComMovimentacoes,
    ProdutoNaoEncontrado,
)
from app.models.enums import CategoriaProduto, UnidadeMedida
from app.models.produto import ProdutoORM
from app.repositories.produto import RepositorioDeProdutos

CODIGO_MAXIMO = 20
NOME_MAXIMO = 100
DESCRICAO_MAXIMA = 200
CATEGORIA_MAXIMA = 50
ESTOQUE_MINIMO_MAXIMO = 999_999
# Data URL de uma imagem de ~400 KB em base64.
CATEGORIAS_DISPONIVEIS = [categoria.value for categoria in CategoriaProduto]
FOTO_MAXIMA = 600_000


def _normalizar_e_validar(
    codigo: str, nome: str, descricao: str, categoria: str, estoque_minimo: int
) -> tuple[str, str, str, str]:
    codigo = (codigo or "").strip().upper()
    nome = (nome or "").strip()
    descricao = (descricao or "").strip()

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
    try:
        categoria = CategoriaProduto(categoria)
    except ValueError as erro:
        validas = ", ".join(c.value for c in CategoriaProduto)
        raise DadosInvalidos(f"Categoria inválida. Use uma destas: {validas}") from erro
    if estoque_minimo < 0:
        raise DadosInvalidos("O estoque mínimo não pode ser negativo")
    if estoque_minimo > ESTOQUE_MINIMO_MAXIMO:
        raise DadosInvalidos(f"O estoque mínimo não pode passar de {ESTOQUE_MINIMO_MAXIMO}")

    return codigo, nome, descricao, categoria


def _validar_foto(foto: str) -> str:
    """A imagem chega embutida como data URL; aqui so conferimos forma e tamanho."""
    foto = (foto or "").strip()
    if not foto:
        return ""
    if not foto.startswith("data:image/"):
        raise DadosInvalidos("O arquivo enviado nao e uma imagem")
    if len(foto) > FOTO_MAXIMA:
        raise DadosInvalidos("A imagem e grande demais; use uma de ate 400 KB")
    return foto


def _garantir_codigo_livre(
    repo: RepositorioDeProdutos, codigo: str, produto_id: int | None = None
) -> None:
    existente = repo.buscar_por_codigo(codigo)
    if existente is not None and existente.id != produto_id:
        raise CodigoJaExiste(codigo)


def criar_produto(
    repo: RepositorioDeProdutos,
    almoxarifado_id: int,
    codigo: str,
    nome: str,
    categoria: str,
    unidade: UnidadeMedida,
    descricao: str = "",
    estoque_minimo: int = 0,
    foto: str = "",
) -> ProdutoORM:
    codigo, nome, descricao, categoria = _normalizar_e_validar(
        codigo, nome, descricao, categoria, estoque_minimo
    )
    _garantir_codigo_livre(repo, codigo)
    foto = _validar_foto(foto)

    return repo.adicionar(
        almoxarifado_id=almoxarifado_id,
        codigo=codigo,
        nome=nome,
        descricao=descricao,
        categoria=categoria,
        unidade=unidade,
        estoque_minimo=estoque_minimo,
        foto=foto,
        saldo=0,
    )


def obter_produto(repo: RepositorioDeProdutos, produto_id: int) -> ProdutoORM:
    produto = repo.buscar(produto_id)
    if produto is None:
        raise ProdutoNaoEncontrado(produto_id)
    return produto


def listar_produtos(
    repo: RepositorioDeProdutos,
    almoxarifado_id: int | None = None,
    categoria: str | None = None,
    apenas_abaixo_do_minimo: bool = False,
) -> list[ProdutoORM]:
    return repo.listar(almoxarifado_id, categoria, apenas_abaixo_do_minimo)


def listar_categorias(repo: RepositorioDeProdutos, almoxarifado_id: int | None = None) -> list[str]:
    return repo.categorias(almoxarifado_id)


def atualizar_produto(
    repo: RepositorioDeProdutos,
    produto_id: int,
    almoxarifado_id: int | None = None,
    codigo: str | None = None,
    nome: str | None = None,
    descricao: str | None = None,
    categoria: str | None = None,
    unidade: UnidadeMedida | None = None,
    estoque_minimo: int | None = None,
    foto: str | None = None,
) -> ProdutoORM:
    produto = obter_produto(repo, produto_id)

    novo_almoxarifado = produto.almoxarifado_id if almoxarifado_id is None else almoxarifado_id
    novo_codigo = produto.codigo if codigo is None else codigo
    novo_nome = produto.nome if nome is None else nome
    nova_descricao = produto.descricao if descricao is None else descricao
    nova_categoria = produto.categoria if categoria is None else categoria
    nova_unidade = produto.unidade if unidade is None else unidade
    novo_minimo = produto.estoque_minimo if estoque_minimo is None else estoque_minimo
    nova_foto = _validar_foto(produto.foto if foto is None else foto)

    novo_codigo, novo_nome, nova_descricao, nova_categoria = _normalizar_e_validar(
        novo_codigo, novo_nome, nova_descricao, nova_categoria, novo_minimo
    )
    _garantir_codigo_livre(repo, novo_codigo, produto_id)

    return repo.atualizar(
        produto,
        almoxarifado_id=novo_almoxarifado,
        codigo=novo_codigo,
        nome=novo_nome,
        descricao=nova_descricao,
        categoria=nova_categoria,
        unidade=nova_unidade,
        estoque_minimo=novo_minimo,
        foto=nova_foto,
    )


def remover_produto(repo: RepositorioDeProdutos, produto_id: int) -> None:
    produto = obter_produto(repo, produto_id)
    if repo.tem_movimentacoes(produto):
        raise ProdutoComMovimentacoes(produto_id)
    repo.remover(produto)
