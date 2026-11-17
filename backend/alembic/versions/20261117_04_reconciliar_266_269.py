"""Une retenção/acessos #266 e ciência dos Termos #269, sem apagar dados."""

from alembic import op
import sqlalchemy as sa

revision = "20261117_04"
down_revision = ("20261117_03", "20261117_02")
branch_labels = None
depends_on = None


def upgrade():
    # O antigo ID 20261117_02 também foi usado pela retenção na branch #266.
    # Nesse histórico, Alembic pode considerar ciência aplicada sem suas colunas.
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("usuarios")}
    if "termos_versao" not in colunas:
        op.add_column("usuarios", sa.Column("termos_versao", sa.String(32), nullable=True))
    if "termos_ciencia_em" not in colunas:
        op.add_column(
            "usuarios", sa.Column("termos_ciencia_em", sa.DateTime(timezone=True), nullable=True)
        )
    checks = {c["name"] for c in sa.inspect(op.get_bind()).get_check_constraints("usuarios")}
    if "ck_usuario_ciencia_termos_completa" not in checks:
        op.create_check_constraint(
            "ck_usuario_ciencia_termos_completa",
            "usuarios",
            "(termos_versao IS NULL AND termos_ciencia_em IS NULL) OR (termos_versao IS NOT NULL AND termos_versao <> '' AND termos_ciencia_em IS NOT NULL)",
        )


def downgrade():
    # Os pais mantêm seus dados/colunas; retirar a união não apaga ciência real.
    pass
