"""Open reports and one-time acknowledgements (RF21).

Revision ID: 20261101_02
Revises: 20261101_01
"""
from alembic import op
import sqlalchemy as sa

revision = "20261101_02"
down_revision = "20261101_01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "denuncias",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("comentario_versao_id", sa.Uuid(), sa.ForeignKey("comentario_versoes.id"), nullable=False),
        sa.Column("denunciante_id", sa.Uuid(), sa.ForeignKey("usuarios.id")),
        sa.Column("motivo", sa.Enum("OFENSA_PESSOAL", "XINGAMENTO", "PALAVRAO", "AMEACA", "DISCRIMINACAO", "EXPOSICAO_DADOS_PESSOAIS", "SPAM", name="motivo_denuncia", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("comentario_versao_id", "denunciante_id", name="uq_denuncia_conta_versao"),
    )
    op.create_table(
        "agradecimentos",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("comentario_versao_id", sa.Uuid(), sa.ForeignKey("comentario_versoes.id"), nullable=False),
        sa.Column("evento", sa.Enum("SUSPENSAO", "REMOCAO", name="evento_agradecimento", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_agradecimentos_usuario_id", "agradecimentos", ["usuario_id"])


def downgrade():
    op.drop_table("agradecimentos")
    op.drop_table("denuncias")
