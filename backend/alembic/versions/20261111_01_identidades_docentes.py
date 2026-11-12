"""Identidade institucional, fila privada e permissão separada (#207)."""

from alembic import op
import sqlalchemy as sa

revision = "20261111_01"
down_revision = "20261107_01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "usuarios",
        sa.Column("reconciliador", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "identidades_docentes",
        sa.Column("identificador", sa.String(30), primary_key=True),
        sa.Column(
            "professor_id", sa.Uuid(), sa.ForeignKey("professores.id"), unique=True, nullable=False
        ),
        sa.Column("nome", sa.String(150), nullable=False),
    )
    op.create_table(
        "pendencias_identidade",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("chave", sa.String(255), unique=True, nullable=False),
        sa.Column("professor_id", sa.Uuid(), sa.ForeignKey("professores.id"), nullable=False),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("unidade", sa.String(100), nullable=False),
        sa.Column("periodo", sa.String(10), nullable=False),
        sa.Column("disciplina", sa.String(30), nullable=False),
        sa.Column("turma", sa.String(30), nullable=False),
        sa.Column("motivo", sa.String(80), nullable=False),
        sa.Column("candidatos", sa.JSON(), nullable=False),
        sa.Column("estado", sa.String(15), nullable=False),
        sa.Column("identificador_destino", sa.String(30)),
        sa.Column("versao", sa.Integer(), nullable=False),
        sa.Column("humana", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "estado IN ('PENDENTE','CONFIRMADA','SEPARADA','APLICADA')",
            name="ck_pendencia_identidade_estado",
        ),
    )
    op.create_table(
        "decisoes_identidade",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "pendencia_id", sa.Uuid(), sa.ForeignKey("pendencias_identidade.id"), nullable=False
        ),
        sa.Column("usuario_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("acao", sa.String(15), nullable=False),
        sa.Column("justificativa", sa.String(500), nullable=False),
        sa.Column("identificador", sa.String(30)),
        sa.Column("versao", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_decisoes_identidade_pendencia_id", "decisoes_identidade", ["pendencia_id"])


def downgrade():
    if op.get_bind().scalar(
        sa.text("SELECT count(*) FROM identidades_docentes")
    ) or op.get_bind().scalar(sa.text("SELECT count(*) FROM pendencias_identidade")):
        raise RuntimeError(
            "Existem identidades/auditoria: restaurar backup completo; não descartar associações."
        )
    op.drop_index("ix_decisoes_identidade_pendencia_id", table_name="decisoes_identidade")
    op.drop_table("decisoes_identidade")
    op.drop_table("pendencias_identidade")
    op.drop_table("identidades_docentes")
    op.drop_column("usuarios", "reconciliador")
