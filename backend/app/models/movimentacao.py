from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import TipoMovimentacao
from app.models.produto import ProdutoORM


class MovimentacaoORM(Base):
    """Registro de entrada ou saída de um produto. Livro-razão do estoque."""

    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        SAEnum(
            TipoMovimentacao,
            native_enum=False,
            length=10,
            values_callable=lambda enum: [membro.value for membro in enum],
        ),
        nullable=False,
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    responsavel: Mapped[str] = mapped_column(String(100), nullable=False)
    requerente: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    destino: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    observacao: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    produto: Mapped[ProdutoORM] = relationship(back_populates="movimentacoes")
