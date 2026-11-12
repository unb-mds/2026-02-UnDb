"""Explicit professor correspondence; no automatic data reconciliation.

Revision ID: 20261107_01
Revises: 20261101_03
"""

from alembic import op
import sqlalchemy as sa

revision = "20261107_01"
down_revision = "20261101_03"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "professor_correspondencias",
        sa.Column("origem_id", sa.Uuid(), sa.ForeignKey("professores.id"), primary_key=True),
        sa.Column("destino_id", sa.Uuid(), sa.ForeignKey("professores.id"), nullable=False),
        sa.Column("evidencia", sa.String(500), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("origem_id <> destino_id", name="ck_correspondencia_distinta"),
        sa.CheckConstraint("length(trim(evidencia)) > 0", name="ck_correspondencia_evidencia"),
    )
    op.create_index(
        "ix_professor_correspondencias_destino_id", "professor_correspondencias", ["destino_id"]
    )


def downgrade():
    connection = op.get_bind()
    if connection.scalar(sa.text("SELECT count(*) FROM professor_correspondencias")):
        raise RuntimeError(
            "Há reconciliações aplicadas: restaurar backup completo antes do downgrade."
        )
    op.drop_index(
        "ix_professor_correspondencias_destino_id", table_name="professor_correspondencias"
    )
    op.drop_table("professor_correspondencias")
