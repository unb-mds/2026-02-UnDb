"""Fallback docente por nome e unidade, sem reconciliação automática (#207)."""

from alembic import op
import sqlalchemy as sa

revision = "20261113_01"
down_revision = "20261111_01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "identidades_locais",
        sa.Column("nome_normalizado", sa.String(150), primary_key=True),
        sa.Column("unidade", sa.String(100), primary_key=True),
        sa.Column("professor_id", sa.Uuid(), sa.ForeignKey("professores.id"), nullable=False),
    )


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT count(*) FROM identidades_locais")):
        raise RuntimeError("Existem associações locais: preservar auditoria e restaurar backup.")
    op.drop_table("identidades_locais")
