"""Contadores compartilhados e descartáveis para prevenção de abuso (#266, bloco 1)."""

from alembic import op
import sqlalchemy as sa

revision = "20261117_01"
down_revision = "20261115_02"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "contadores_abuso",
        sa.Column("operacao", sa.String(64), primary_key=True),
        sa.Column("chave", sa.String(64), primary_key=True),
        sa.Column("quantidade", sa.BigInteger(), nullable=False),
        sa.Column("inicio_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("proxima_tentativa_em", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("quantidade > 0", name="ck_contador_abuso_quantidade"),
        sa.CheckConstraint("length(chave) = 64", name="ck_contador_abuso_chave"),
        sa.CheckConstraint("expira_em > inicio_em", name="ck_contador_abuso_janela"),
        prefixes=["UNLOGGED"] if op.get_context().dialect.name == "postgresql" else [],
    )
    op.create_index("ix_contadores_abuso_expira_em", "contadores_abuso", ["expira_em"])


def downgrade():
    op.drop_index("ix_contadores_abuso_expira_em", table_name="contadores_abuso")
    op.drop_table("contadores_abuso")
