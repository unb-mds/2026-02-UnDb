"""Permite identificar decisões do sistema sem atribuí-las a uma pessoa (#239)."""

from alembic import op
import sqlalchemy as sa

revision = "20261114_01"
down_revision = "20261113_01"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("decisoes_moderacao", "moderador_id", existing_type=sa.Uuid(), nullable=True)


def downgrade():
    if op.get_bind().scalar(
        sa.text("SELECT count(*) FROM decisoes_moderacao WHERE moderador_id IS NULL")
    ):
        raise RuntimeError(
            "Preservar auditoria automática; aguardar descarte vigente antes do downgrade."
        )
    op.alter_column("decisoes_moderacao", "moderador_id", existing_type=sa.Uuid(), nullable=False)
