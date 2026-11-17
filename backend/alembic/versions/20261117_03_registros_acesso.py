"""Registros de acesso privados (#266/bloco 6)."""

from alembic import op
import sqlalchemy as sa

revision = "20261117_03_acessos"
down_revision = "20261117_02_retencao"
branch_labels = None
depends_on = None


def upgrade():
    # Bancos anteriores da #266 podem ter acesso sob o ID agora usado pela #278.
    if sa.inspect(op.get_bind()).has_table("registros_acesso"):
        return
    op.create_table(
        "registros_acesso",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("ocorrido_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("operacao", sa.String(80), nullable=False),
        sa.Column("usuario_id", sa.Uuid()),
        sa.Column("ip_conexao", sa.Text()),
        sa.Column("encaminhado_nao_confiavel", sa.Text()),
        sa.Column("resultado", sa.String(10), nullable=False),
        sa.Column("requisicao_id", sa.Uuid(), nullable=False),
    )
    op.create_index("ix_registros_acesso_expira_em", "registros_acesso", ["expira_em"])


def downgrade():
    op.drop_index("ix_registros_acesso_expira_em", table_name="registros_acesso")
    op.drop_table("registros_acesso")
