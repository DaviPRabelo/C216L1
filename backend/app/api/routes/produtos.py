from fastapi import APIRouter, Depends, Query

from app.api.dependencias import obter_repositorio_de_produtos
from app.repositories.produto import RepositorioDeProdutos
from app.schemas.produto import Produto, ProdutoAtualizacao, ProdutoEntrada
from app.services import produto as servico

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("", response_model=list[Produto])
def listar(
    categoria: str | None = Query(default=None, description="Filtra por categoria"),
    abaixo_do_minimo: bool = Query(default=False, description="Só itens em falta"),
    repo: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos),
):
    return servico.listar_produtos(repo, categoria, abaixo_do_minimo)


@router.get("/categorias", response_model=list[str])
def categorias(repo: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos)):
    return servico.listar_categorias(repo)


@router.get("/{produto_id}", response_model=Produto)
def obter(produto_id: int, repo: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos)):
    return servico.obter_produto(repo, produto_id)


@router.post("", response_model=Produto, status_code=201)
def criar(
    entrada: ProdutoEntrada,
    repo: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos),
):
    return servico.criar_produto(
        repo,
        codigo=entrada.codigo,
        nome=entrada.nome,
        categoria=entrada.categoria,
        unidade=entrada.unidade,
        descricao=entrada.descricao,
        estoque_minimo=entrada.estoque_minimo,
    )


@router.put("/{produto_id}", response_model=Produto)
def substituir(
    produto_id: int,
    entrada: ProdutoEntrada,
    repo: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos),
):
    return servico.atualizar_produto(
        repo,
        produto_id,
        codigo=entrada.codigo,
        nome=entrada.nome,
        descricao=entrada.descricao,
        categoria=entrada.categoria,
        unidade=entrada.unidade,
        estoque_minimo=entrada.estoque_minimo,
    )


@router.patch("/{produto_id}", response_model=Produto)
def atualizar(
    produto_id: int,
    entrada: ProdutoAtualizacao,
    repo: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos),
):
    return servico.atualizar_produto(repo, produto_id, **entrada.model_dump(exclude_unset=True))


@router.delete("/{produto_id}", status_code=204)
def remover(produto_id: int, repo: RepositorioDeProdutos = Depends(obter_repositorio_de_produtos)):
    servico.remover_produto(repo, produto_id)
