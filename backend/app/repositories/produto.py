from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.produto import ProdutoORM


class RepositorioDeProdutos:
    """Acesso aos dados de produtos. Única camada que conhece o SQLAlchemy."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, **campos) -> ProdutoORM:
        produto = ProdutoORM(**campos)
        self._sessao.add(produto)
        self._sessao.commit()
        self._sessao.refresh(produto)
        return produto

    def buscar(self, produto_id: int) -> ProdutoORM | None:
        return self._sessao.get(ProdutoORM, produto_id)

    def buscar_por_codigo(self, codigo: str) -> ProdutoORM | None:
        return self._sessao.scalars(select(ProdutoORM).where(ProdutoORM.codigo == codigo)).first()

    def listar(
        self, categoria: str | None = None, apenas_abaixo_do_minimo: bool = False
    ) -> list[ProdutoORM]:
        consulta = select(ProdutoORM).order_by(ProdutoORM.nome)
        if categoria:
            consulta = consulta.where(ProdutoORM.categoria == categoria)
        if apenas_abaixo_do_minimo:
            consulta = consulta.where(ProdutoORM.saldo < ProdutoORM.estoque_minimo)
        return list(self._sessao.scalars(consulta))

    def categorias(self) -> list[str]:
        return list(
            self._sessao.scalars(
                select(ProdutoORM.categoria).distinct().order_by(ProdutoORM.categoria)
            )
        )

    def atualizar(self, produto: ProdutoORM, **campos) -> ProdutoORM:
        for campo, valor in campos.items():
            setattr(produto, campo, valor)
        self._sessao.commit()
        self._sessao.refresh(produto)
        return produto

    def remover(self, produto: ProdutoORM) -> None:
        self._sessao.delete(produto)
        self._sessao.commit()

    def tem_movimentacoes(self, produto: ProdutoORM) -> bool:
        return len(produto.movimentacoes) > 0
