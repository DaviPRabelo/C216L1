from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import StatusInventario

if TYPE_CHECKING:
    from app.models.produto import ProdutoORM


class InventarioORM(Base):
    """Contagem física do estoque de um almoxarifado numa data."""

    __tablename__ = "inventarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    almoxarifado_id: Mapped[int] = mapped_column(
        ForeignKey("almoxarifados.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    responsavel: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[StatusInventario] = mapped_column(
        SAEnum(
            StatusInventario,
            native_enum=False,
            length=10,
            values_callable=lambda enum: [membro.value for membro in enum],
        ),
        nullable=False,
        default=StatusInventario.ABERTO,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    itens: Mapped[list["ContagemItemORM"]] = relationship(
        back_populates="inventario",
        cascade="all, delete-orphan",
        order_by="ContagemItemORM.id",
    )

    @property
    def aberto(self) -> bool:
        return self.status is StatusInventario.ABERTO

    @property
    def itens_contados(self) -> int:
        return sum(1 for item in self.itens if item.quantidade_contada is not None)

    @property
    def itens_divergentes(self) -> int:
        return sum(1 for item in self.itens if item.divergencia not in (None, 0))


class ContagemItemORM(Base):
    """Linha da contagem: o que o sistema dizia e o que foi contado."""

    __tablename__ = "contagens_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventario_id: Mapped[int] = mapped_column(
        ForeignKey("inventarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Congelado na abertura: é contra este número que a contagem é comparada.
    saldo_sistema: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_contada: Mapped[int | None] = mapped_column(Integer, nullable=True)

    inventario: Mapped[InventarioORM] = relationship(back_populates="itens")
    produto: Mapped["ProdutoORM"] = relationship()

    @property
    def produto_codigo(self) -> str:
        return self.produto.codigo

    @property
    def produto_nome(self) -> str:
        return self.produto.nome

    @property
    def unidade(self) -> str:
        return self.produto.unidade

    @property
    def contado(self) -> bool:
        return self.quantidade_contada is not None

    @property
    def divergencia(self) -> int | None:
        if self.quantidade_contada is None:
            return None
        return self.quantidade_contada - self.saldo_sistema
