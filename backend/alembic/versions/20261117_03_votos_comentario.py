"""Votos de utilidade por conta e versão (#278)."""

from alembic import op
import sqlalchemy as sa

revision = "20261117_03"
down_revision = "20261117_02"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "votos_comentario",
        sa.Column("comentario_versao_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("voto", sa.String(8), nullable=False),
        sa.PrimaryKeyConstraint("comentario_versao_id", "usuario_id"),
        sa.ForeignKeyConstraint(
            ["comentario_versao_id"], ["comentario_versoes.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.CheckConstraint("voto IN ('UTIL', 'NAO_UTIL')", name="ck_voto_comentario_valor"),
    )
    op.create_index("ix_votos_comentario_usuario_id", "votos_comentario", ["usuario_id"])


def downgrade():
    op.drop_index("ix_votos_comentario_usuario_id", table_name="votos_comentario")
    op.drop_table("votos_comentario")
