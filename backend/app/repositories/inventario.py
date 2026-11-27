from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import StatusInventario
from app.models.inventario import ContagemItemORM, InventarioORM
from app.models.produto import ProdutoORM


class RepositorioDeInventarios:
    """Acesso aos dados de inventários e suas contagens."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def _consulta_completa(self):
        return select(InventarioORM).options(
            selectinload(InventarioORM.itens).selectinload(ContagemItemORM.produto)
        )

    def abrir(
        self, almoxarifado_id: int, data: date, responsavel: str, produtos: list[ProdutoORM]
    ) -> InventarioORM:
        """Cria o inventário e congela o saldo atual de cada produto."""
        inventario = InventarioORM(
            almoxarifado_id=almoxarifado_id,
            data=data,
            responsavel=responsavel,
            status=StatusInventario.ABERTO,
        )
        inventario.itens = [
            ContagemItemORM(produto_id=produto.id, saldo_sistema=produto.saldo)
            for produto in produtos
        ]
        self._sessao.add(inventario)
        self._sessao.commit()
        return self.buscar(inventario.id)

    def buscar(self, inventario_id: int) -> InventarioORM | None:
        return self._sessao.scalars(
            self._consulta_completa().where(InventarioORM.id == inventario_id)
        ).first()

    def buscar_aberto(self, almoxarifado_id: int) -> InventarioORM | None:
        return self._sessao.scalars(
            self._consulta_completa()
            .where(InventarioORM.almoxarifado_id == almoxarifado_id)
            .where(InventarioORM.status == StatusInventario.ABERTO)
        ).first()

    def listar(self, almoxarifado_id: int | None = None) -> list[InventarioORM]:
        consulta = self._consulta_completa().order_by(InventarioORM.id.desc())
        if almoxarifado_id is not None:
            consulta = consulta.where(InventarioORM.almoxarifado_id == almoxarifado_id)
        return list(self._sessao.scalars(consulta))

    def registrar_contagem(self, item: ContagemItemORM, quantidade: int) -> ContagemItemORM:
        item.quantidade_contada = quantidade
        self._sessao.commit()
        self._sessao.refresh(item)
        return item

    def fechar(self, inventario: InventarioORM) -> InventarioORM:
        inventario.status = StatusInventario.FECHADO
        self._sessao.commit()
        return self.buscar(inventario.id)
