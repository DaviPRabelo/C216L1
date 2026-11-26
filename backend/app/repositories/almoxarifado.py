from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.almoxarifado import AlmoxarifadoORM
from app.models.produto import ProdutoORM


class RepositorioDeAlmoxarifados:
    """Acesso aos dados de almoxarifados."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, **campos) -> AlmoxarifadoORM:
        almoxarifado = AlmoxarifadoORM(**campos)
        self._sessao.add(almoxarifado)
        self._sessao.commit()
        self._sessao.refresh(almoxarifado)
        return almoxarifado

    def buscar(self, almoxarifado_id: int) -> AlmoxarifadoORM | None:
        return self._sessao.get(AlmoxarifadoORM, almoxarifado_id)

    def buscar_por_nome(self, nome: str) -> AlmoxarifadoORM | None:
        return self._sessao.scalars(
            select(AlmoxarifadoORM).where(func.lower(AlmoxarifadoORM.nome) == nome.lower())
        ).first()

    def listar(self, apenas_ativos: bool = False) -> list[AlmoxarifadoORM]:
        consulta = select(AlmoxarifadoORM).order_by(AlmoxarifadoORM.nome)
        if apenas_ativos:
            consulta = consulta.where(AlmoxarifadoORM.ativo.is_(True))
        return list(self._sessao.scalars(consulta))

    def atualizar(self, almoxarifado: AlmoxarifadoORM, **campos) -> AlmoxarifadoORM:
        for campo, valor in campos.items():
            setattr(almoxarifado, campo, valor)
        self._sessao.commit()
        self._sessao.refresh(almoxarifado)
        return almoxarifado

    def remover(self, almoxarifado: AlmoxarifadoORM) -> None:
        self._sessao.delete(almoxarifado)
        self._sessao.commit()

    def contar_produtos(self, almoxarifado_id: int) -> int:
        return self._sessao.scalar(
            select(func.count(ProdutoORM.id)).where(ProdutoORM.almoxarifado_id == almoxarifado_id)
        )

    def resumo(self, almoxarifado_id: int) -> tuple[int, int, int]:
        """Devolve (total de produtos, produtos em falta, unidades em estoque)."""
        em_falta = case((ProdutoORM.saldo < ProdutoORM.estoque_minimo, 1), else_=0)
        consulta = select(
            func.count(ProdutoORM.id),
            func.coalesce(func.sum(em_falta), 0),
            func.coalesce(func.sum(ProdutoORM.saldo), 0),
        ).where(ProdutoORM.almoxarifado_id == almoxarifado_id)
        total, falta, unidades = self._sessao.execute(consulta).one()
        return int(total), int(falta), int(unidades)
