"""Create comment versions for RF20.

Revision ID: 20261024_01
Revises: 20260921_01
Create Date: 2026-10-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261024_01"
down_revision: str | Sequence[str] | None = "20260921_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

estado_comentario = sa.Enum(
    "PENDENTE",
    "PUBLICADO",
    "SUSPENSO",
    "REMOVIDO",
    "RETIRADO",
    "SUBSTITUIDO",
    name="estado_comentario",
)


def upgrade() -> None:
    op.create_table(
        "comentario_versoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("avaliacao_id", sa.Uuid(), nullable=False),
        sa.Column("substitui_id", sa.Uuid(), nullable=True),
        sa.Column("texto", sa.String(length=500), nullable=False),
        sa.Column("estado", estado_comentario, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "char_length(texto) BETWEEN 1 AND 500",
            name="ck_comentario_versao_tamanho",
        ),
        sa.ForeignKeyConstraint(["avaliacao_id"], ["avaliacoes.id"]),
        sa.ForeignKeyConstraint(["substitui_id"], ["comentario_versoes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("comentario_versoes")
    estado_comentario.drop(op.get_bind(), checkfirst=True)
