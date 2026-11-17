"""Une votos #278 e acessos #266, inclusive bancos com o antigo ID ambíguo _03."""

from alembic import op
import sqlalchemy as sa

revision = "20261117_05"
down_revision = ("20261117_04", "20261117_03")
branch_labels = None
depends_on = None


def upgrade():
    # O histórico da #266 carimbava _03 para acessos, sem aplicar votos.
    # Preserve os votos reais; reconstrua apenas o schema ausente nesse histórico.
    if sa.inspect(op.get_bind()).has_table("votos_comentario"):
        return
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
    # Cada pai mantém seu schema; o downgrade da migração de votos o remove.
    pass
