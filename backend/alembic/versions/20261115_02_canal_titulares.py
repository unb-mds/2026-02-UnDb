"""Solicitações de titulares e histórico independente da moderação."""

from alembic import op
import sqlalchemy as sa

revision = "20261115_02"
down_revision = "20261115_01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "solicitacoes_titulares",
        sa.CheckConstraint(
            "categoria IN ('DADO_INCORRETO', 'COMENTARIO_ILICITO', 'NOTA_SUSPEITA', 'FRAUDE_COORDENADA', 'EXPOSICAO_PESSOAL', 'DIREITO_LGPD', 'OUTRA')",
            name="ck_solicitacao_categoria",
        ),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("chave_hash", sa.String(64), nullable=False),
        sa.Column("categoria", sa.String(40), nullable=False),
        sa.Column("alvo", sa.String(1000), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("evidencia", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "eventos_solicitacoes",
        sa.CheckConstraint(
            "(tipo = 'COMPLEMENTO' AND autor_id IS NULL) OR (tipo IN ('TRIAGEM', 'PROVIDENCIA', 'RESPOSTA') AND autor_id IS NOT NULL)",
            name="ck_evento_tipo_autor",
        ),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "solicitacao_id", sa.Uuid(), sa.ForeignKey("solicitacoes_titulares.id"), nullable=False
        ),
        sa.Column("autor_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_eventos_solicitacoes_solicitacao_id", "eventos_solicitacoes", ["solicitacao_id"]
    )


def downgrade():
    op.drop_table("eventos_solicitacoes")
    op.drop_table("solicitacoes_titulares")
