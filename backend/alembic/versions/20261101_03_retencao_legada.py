"""Apply approved retention to comments withdrawn before moderation integration.

Revision ID: 20261101_03
Revises: 20261101_02
"""
from alembic import op

revision = "20261101_03"
down_revision = "20261101_02"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""UPDATE comentario_versoes
        SET descartar_em = updated_at + INTERVAL '7 days'
        WHERE estado IN ('RETIRADO', 'REMOVIDO') AND texto IS NOT NULL AND descartar_em IS NULL""")
    op.execute("""UPDATE comentario_versoes SET texto = NULL, descartar_em = NULL
        WHERE descartar_em <= CURRENT_TIMESTAMP AND estado IN ('RETIRADO', 'REMOVIDO')""")


def downgrade():
    # Data discarded under the approved policy cannot be recreated.
    pass
