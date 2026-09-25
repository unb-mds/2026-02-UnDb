"""Create the import execution history.

Revision ID: 20260920_01
Revises: 20260919_03
Create Date: 2026-09-20
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260920_01"
down_revision: str | Sequence[str] | None = "20260919_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "importacao_execucoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "iniciada_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "finalizada_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("ano", sa.String(length=4), nullable=False),
        sa.Column("periodo", sa.String(length=2), nullable=False),
        sa.Column("departamentos", sa.JSON(), nullable=False),
        sa.Column(
            "ofertas_extraidas",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "ofertas_processadas",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("erro", sa.Text(), nullable=True),
        sa.Column("resultado_json", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("importacao_execucoes")
