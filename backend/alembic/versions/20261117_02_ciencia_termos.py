"""Registra ciência dos Termos sem atribuí-la retroativamente a contas antigas."""

from alembic import op
import sqlalchemy as sa

revision = "20261117_02"
down_revision = "20261115_02"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("usuarios") as batch:
        batch.add_column(sa.Column("termos_versao", sa.String(32), nullable=True))
        batch.add_column(sa.Column("termos_ciencia_em", sa.DateTime(timezone=True), nullable=True))
        batch.create_check_constraint(
            "ck_usuario_ciencia_termos_completa",
            "(termos_versao IS NULL AND termos_ciencia_em IS NULL) OR "
            "(termos_versao IS NOT NULL AND termos_versao <> '' AND termos_ciencia_em IS NOT NULL)",
        )


def downgrade():
    with op.batch_alter_table("usuarios") as batch:
        batch.drop_constraint("ck_usuario_ciencia_termos_completa", type_="check")
        batch.drop_column("termos_ciencia_em")
        batch.drop_column("termos_versao")
