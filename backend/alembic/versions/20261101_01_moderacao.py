"""Moderation permission, decisions and comment text retention.

Revision ID: 20261101_01
Revises: 20261024_01
"""

from alembic import op
import sqlalchemy as sa

revision = "20261101_01"
down_revision = "20261024_01"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE estado_comentario ADD VALUE IF NOT EXISTS 'REJEITADO'")
    op.add_column(
        "usuarios", sa.Column("moderador", sa.Boolean(), server_default=sa.false(), nullable=False)
    )
    op.alter_column("comentario_versoes", "texto", existing_type=sa.String(500), nullable=True)
    op.add_column("comentario_versoes", sa.Column("descartar_em", sa.DateTime(timezone=True)))
    op.create_index("ix_comentario_versoes_descartar_em", "comentario_versoes", ["descartar_em"])
    op.create_check_constraint(
        "ck_comentario_texto_ativo",
        "comentario_versoes",
        "estado NOT IN ('PENDENTE', 'PUBLICADO', 'SUSPENSO') OR texto IS NOT NULL",
    )
    op.create_table(
        "decisoes_moderacao",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "comentario_versao_id",
            sa.Uuid(),
            sa.ForeignKey("comentario_versoes.id"),
            nullable=False,
        ),
        sa.Column("moderador_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("acao", sa.String(20), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("estado_anterior", sa.String(20), nullable=False),
        sa.Column("estado_posterior", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("descartar_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_decisoes_moderacao_comentario_versao_id", "decisoes_moderacao", ["comentario_versao_id"]
    )
    op.create_index("ix_decisoes_moderacao_descartar_em", "decisoes_moderacao", ["descartar_em"])


def downgrade():
    # A downgrade must never fabricate discarded content or silently lose versions.
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM comentario_versoes WHERE texto IS NULL OR estado::text = 'REJEITADO')
        THEN RAISE EXCEPTION 'Downgrade recusado: existem textos descartados/versoes rejeitadas';
        END IF; END $$""")
    op.drop_table("decisoes_moderacao")
    op.drop_constraint("ck_comentario_texto_ativo", "comentario_versoes", type_="check")
    op.drop_index("ix_comentario_versoes_descartar_em", table_name="comentario_versoes")
    op.drop_column("comentario_versoes", "descartar_em")
    op.alter_column("comentario_versoes", "texto", existing_type=sa.String(500), nullable=False)
    op.drop_column("usuarios", "moderador")
    op.execute("ALTER TYPE estado_comentario RENAME TO estado_comentario_old")
    op.execute(
        "CREATE TYPE estado_comentario AS ENUM ('PENDENTE', 'PUBLICADO', 'SUSPENSO', 'REMOVIDO', 'RETIRADO', 'SUBSTITUIDO')"
    )
    op.execute(
        "ALTER TABLE comentario_versoes ALTER COLUMN estado TYPE estado_comentario USING estado::text::estado_comentario"
    )
    op.execute("DROP TYPE estado_comentario_old")
