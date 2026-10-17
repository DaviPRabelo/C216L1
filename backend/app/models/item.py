from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ItemORM(Base):
    """Modelo ORM do item. Mapeia a tabela `itens`."""

    __tablename__ = "itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    preco: Mapped[float] = mapped_column(Float, nullable=False)
