from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import UsuarioORM


class AlmoxarifadoORM(Base):
    """Depósito físico onde os produtos são guardados."""

    __tablename__ = "almoxarifados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    local: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    # O responsavel e um operador cadastrado, nao um texto livre.
    responsavel_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    responsavel: Mapped["UsuarioORM | None"] = relationship(lazy="joined")

    @property
    def responsavel_nome(self) -> str:
        return self.responsavel.nome if self.responsavel else ""
