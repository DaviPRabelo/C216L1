"""papel do usuario, categorias fixas e responsavel do almoxarifado

Revision ID: 827cd3378c27
Revises: f511b570601e
Create Date: 2026-11-28 10:38:38.722900

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "827cd3378c27"
down_revision: str | Sequence[str] | None = "f511b570601e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FK_RESPONSAVEL = "almoxarifados_responsavel_id_fkey"

CATEGORIAS = (
    "Ferramentas",
    "Fixadores",
    "EPI",
    "Elétrica",
    "Hidráulica",
    "Limpeza",
    "Papelaria",
    "Construção",
    "Outros",
)

categoria_enum = sa.Enum(*CATEGORIAS, name="categoriaproduto", native_enum=False, length=20)
papel_enum = sa.Enum(
    "ADMIN", "GERENTE", "EMPREGADO", name="papelusuario", native_enum=False, length=10
)


def upgrade() -> None:
    """Upgrade schema."""
    # O responsável deixa de ser texto livre e passa a apontar para um usuário.
    op.add_column("almoxarifados", sa.Column("responsavel_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_almoxarifados_responsavel_id"),
        "almoxarifados",
        ["responsavel_id"],
        unique=False,
    )
    op.create_foreign_key(
        FK_RESPONSAVEL,
        "almoxarifados",
        "usuarios",
        ["responsavel_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_column("almoxarifados", "responsavel")

    # A categoria sai de texto livre para a lista fixa do domínio.
    op.alter_column(
        "produtos",
        "categoria",
        existing_type=sa.VARCHAR(length=50),
        type_=categoria_enum,
        existing_nullable=False,
    )
    op.create_index(op.f("ix_produtos_categoria"), "produtos", ["categoria"], unique=False)

    # Entra com default para preencher quem já estava cadastrado...
    op.add_column(
        "usuarios",
        sa.Column("papel", papel_enum, nullable=False, server_default="EMPREGADO"),
    )
    # ...e perde o default, para que a aplicação sempre informe o papel.
    op.alter_column("usuarios", "papel", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("usuarios", "papel")

    op.drop_index(op.f("ix_produtos_categoria"), table_name="produtos")
    op.alter_column(
        "produtos",
        "categoria",
        existing_type=categoria_enum,
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
    )

    # Volta o texto livre com default, já que a coluna é obrigatória.
    op.add_column(
        "almoxarifados",
        sa.Column("responsavel", sa.VARCHAR(length=100), nullable=False, server_default=""),
    )
    op.alter_column("almoxarifados", "responsavel", server_default=None)
    op.drop_constraint(FK_RESPONSAVEL, "almoxarifados", type_="foreignkey")
    op.drop_index(op.f("ix_almoxarifados_responsavel_id"), table_name="almoxarifados")
    op.drop_column("almoxarifados", "responsavel_id")
