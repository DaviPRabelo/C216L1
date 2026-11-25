from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import TipoMovimentacao
from app.models.movimentacao import MovimentacaoORM
from app.models.produto import ProdutoORM


class RepositorioDeMovimentacoes:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def registrar(
        self,
        produto: ProdutoORM,
        tipo: TipoMovimentacao,
        quantidade: int,
        responsavel: str,
        observacao: str,
        requerente: str = "",
        destino: str = "",
    ) -> MovimentacaoORM:
        """Grava a movimentação e ajusta o saldo na mesma transação."""
        movimentacao = MovimentacaoORM(
            produto_id=produto.id,
            tipo=tipo,
            quantidade=quantidade,
            responsavel=responsavel,
            observacao=observacao,
            requerente=requerente,
            destino=destino,
        )
        self._sessao.add(movimentacao)

        if tipo is TipoMovimentacao.ENTRADA:
            produto.saldo += quantidade
        else:
            produto.saldo -= quantidade

        self._sessao.commit()
        self._sessao.refresh(movimentacao)
        return movimentacao

    def listar_do_produto(self, produto_id: int) -> list[MovimentacaoORM]:
        return list(
            self._sessao.scalars(
                select(MovimentacaoORM)
                .where(MovimentacaoORM.produto_id == produto_id)
                .order_by(MovimentacaoORM.id.desc())
            )
        )
