from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import UnidadeMedida

if TYPE_CHECKING:
    from app.models.movimentacao import MovimentacaoORM


class ProdutoORM(Base):
    """Item controlado pelo almoxarifado."""

    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    almoxarifado_id: Mapped[int] = mapped_column(
        ForeignKey("almoxarifados.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    unidade: Mapped[UnidadeMedida] = mapped_column(
        SAEnum(
            UnidadeMedida,
            native_enum=False,
            length=3,
            values_callable=lambda enum: [membro.value for membro in enum],
        ),
        nullable=False,
    )
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Imagem embutida como data URL (base64). Vazio quando nao ha foto.
    foto: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Mantido pelo serviço de movimentação, nunca editado diretamente.
    saldo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    movimentacoes: Mapped[list["MovimentacaoORM"]] = relationship(
        back_populates="produto",
        cascade="all, delete-orphan",
        order_by="MovimentacaoORM.id.desc()",
    )

    @property
    def abaixo_do_minimo(self) -> bool:
        return self.saldo < self.estoque_minimo
