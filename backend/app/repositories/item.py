from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import ItemORM


class RepositorioDeItens:
    """Acesso aos dados de itens. Única camada que conhece o SQLAlchemy."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(
        self, nome: str, descricao: str, categoria: str, quantidade: int, preco: float
    ) -> ItemORM:
        item = ItemORM(
            nome=nome,
            descricao=descricao,
            categoria=categoria,
            quantidade=quantidade,
            preco=preco,
        )
        self._sessao.add(item)
        self._sessao.commit()
        self._sessao.refresh(item)
        return item

    def buscar(self, item_id: int) -> ItemORM | None:
        return self._sessao.get(ItemORM, item_id)

    def buscar_por_nome(self, nome: str) -> ItemORM | None:
        return self._sessao.scalars(select(ItemORM).where(ItemORM.nome == nome)).first()

    def listar(self, nome_contem: str | None = None) -> list[ItemORM]:
        consulta = select(ItemORM).order_by(ItemORM.id)
        if nome_contem:
            consulta = consulta.where(ItemORM.nome.ilike(f"%{nome_contem}%"))
        return list(self._sessao.scalars(consulta))

    def atualizar(
        self,
        item: ItemORM,
        nome: str,
        descricao: str,
        categoria: str,
        quantidade: int,
        preco: float,
    ) -> ItemORM:
        item.nome = nome
        item.descricao = descricao
        item.categoria = categoria
        item.quantidade = quantidade
        item.preco = preco
        self._sessao.commit()
        self._sessao.refresh(item)
        return item

    def remover(self, item_id: int) -> bool:
        item = self.buscar(item_id)
        if item is None:
            return False
        self._sessao.delete(item)
        self._sessao.commit()
        return True
