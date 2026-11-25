from datetime import datetime, timezone

import pytest

from app.models.enums import TipoMovimentacao, UnidadeMedida
from app.models.movimentacao import MovimentacaoORM
from app.models.produto import ProdutoORM

PRODUTO_PADRAO = {
    "codigo": "PAR-001",
    "nome": "Parafuso sextavado",
    "categoria": "Fixadores",
    "unidade": UnidadeMedida.UNIDADE,
    "descricao": "M8 x 40mm",
    "estoque_minimo": 50,
}


class RepositorioDeProdutosFalso:
    """Dublê em memória, para os testes unitários rodarem sem banco."""

    def __init__(self) -> None:
        self._produtos: dict[int, ProdutoORM] = {}
        self._proximo_id = 1

    def adicionar(self, **campos) -> ProdutoORM:
        produto = ProdutoORM(id=self._proximo_id, **campos)
        produto.movimentacoes = []
        self._produtos[produto.id] = produto
        self._proximo_id += 1
        return produto

    def buscar(self, produto_id: int) -> ProdutoORM | None:
        return self._produtos.get(produto_id)

    def buscar_por_codigo(self, codigo: str) -> ProdutoORM | None:
        return next((p for p in self._produtos.values() if p.codigo == codigo), None)

    def listar(self, categoria=None, apenas_abaixo_do_minimo=False) -> list[ProdutoORM]:
        produtos = sorted(self._produtos.values(), key=lambda p: p.nome)
        if categoria:
            produtos = [p for p in produtos if p.categoria == categoria]
        if apenas_abaixo_do_minimo:
            produtos = [p for p in produtos if p.saldo < p.estoque_minimo]
        return produtos

    def categorias(self) -> list[str]:
        return sorted({p.categoria for p in self._produtos.values()})

    def atualizar(self, produto: ProdutoORM, **campos) -> ProdutoORM:
        for campo, valor in campos.items():
            setattr(produto, campo, valor)
        return produto

    def remover(self, produto: ProdutoORM) -> None:
        del self._produtos[produto.id]

    def tem_movimentacoes(self, produto: ProdutoORM) -> bool:
        return len(produto.movimentacoes) > 0


class RepositorioDeMovimentacoesFalso:
    def __init__(self) -> None:
        self._movimentacoes: list[MovimentacaoORM] = []
        self._proximo_id = 1

    def registrar(self, produto, tipo, quantidade, responsavel, observacao) -> MovimentacaoORM:
        movimentacao = MovimentacaoORM(
            id=self._proximo_id,
            produto_id=produto.id,
            tipo=tipo,
            quantidade=quantidade,
            responsavel=responsavel,
            observacao=observacao,
            criada_em=datetime.now(timezone.utc),
        )
        self._movimentacoes.append(movimentacao)
        self._proximo_id += 1

        if tipo is TipoMovimentacao.ENTRADA:
            produto.saldo += quantidade
        else:
            produto.saldo -= quantidade

        produto.movimentacoes.append(movimentacao)
        return movimentacao

    def listar_do_produto(self, produto_id: int) -> list[MovimentacaoORM]:
        return [m for m in reversed(self._movimentacoes) if m.produto_id == produto_id]


@pytest.fixture
def repo() -> RepositorioDeProdutosFalso:
    return RepositorioDeProdutosFalso()


@pytest.fixture
def repo_movimentacoes() -> RepositorioDeMovimentacoesFalso:
    return RepositorioDeMovimentacoesFalso()


@pytest.fixture
def produto(repo):
    """Produto já cadastrado, saldo zero."""
    return repo.adicionar(**PRODUTO_PADRAO, saldo=0)