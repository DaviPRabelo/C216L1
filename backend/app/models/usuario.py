from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import PapelUsuario


class UsuarioORM(Base):
    """Operador do almoxarifado."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    setor: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    papel: Mapped[PapelUsuario] = mapped_column(
        SAEnum(
            PapelUsuario,
            native_enum=False,
            length=10,
            values_callable=lambda enum: [membro.value for membro in enum],
        ),
        nullable=False,
        default=PapelUsuario.EMPREGADO,
    )
    senha_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
