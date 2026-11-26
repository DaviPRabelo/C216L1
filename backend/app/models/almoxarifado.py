from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AlmoxarifadoORM(Base):
    """Depósito físico onde os produtos são guardados."""

    __tablename__ = "almoxarifados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    local: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    responsavel: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
