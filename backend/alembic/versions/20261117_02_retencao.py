"""Estados de exclusão e preservação de denúncias encerradas (#266/bloco 5)."""

from alembic import op
import sqlalchemy as sa

revision = "20261117_02_retencao"
down_revision = "20261117_01"
branch_labels = None
depends_on = None


def upgrade():
    def colunas(tabela):
        return {c["name"] for c in sa.inspect(op.get_bind()).get_columns(tabela)}

    if "excluido_em" not in colunas("usuarios"):
        op.add_column("usuarios", sa.Column("excluido_em", sa.DateTime(timezone=True)))
    if sa.inspect(op.get_bind()).has_table("retencao_rollback_contas"):
        op.execute(
            "UPDATE usuarios SET excluido_em=r.excluido_em FROM retencao_rollback_contas r WHERE usuarios.id=r.id"
        )
        op.drop_table("retencao_rollback_contas")
    op.alter_column("usuarios", "password_hash", existing_type=sa.String(255), nullable=True)
    op.execute("UPDATE usuarios SET password_hash=NULL WHERE excluido_em IS NOT NULL")
    if "excluido_em" not in colunas("avaliacoes"):
        op.add_column("avaliacoes", sa.Column("excluido_em", sa.DateTime(timezone=True)))
    if "purgar_em" not in colunas("avaliacoes"):
        op.add_column("avaliacoes", sa.Column("purgar_em", sa.DateTime(timezone=True)))
    if "ix_avaliacoes_purgar_em" not in {
        i["name"] for i in sa.inspect(op.get_bind()).get_indexes("avaliacoes")
    }:
        op.create_index("ix_avaliacoes_purgar_em", "avaliacoes", ["purgar_em"])
    if "encerrada_em" not in colunas("denuncias"):
        op.add_column("denuncias", sa.Column("encerrada_em", sa.DateTime(timezone=True)))
        op.drop_constraint("uq_denuncia_conta_versao", "denuncias", type_="unique")
        op.create_index(
            "uq_denuncia_conta_versao",
            "denuncias",
            ["comentario_versao_id", "denunciante_id"],
            unique=True,
            postgresql_where=sa.text("encerrada_em IS NULL"),
        )


def downgrade():
    # Preserve only IDs/dates across schema rollback/reapply; API must be stopped.
    op.create_table(
        "retencao_rollback_contas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("excluido_em", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute(
        "INSERT INTO retencao_rollback_contas SELECT id, excluido_em FROM usuarios WHERE excluido_em IS NOT NULL"
    )
    # Fechadas não existiam no contrato anterior; não recriar credenciais apagadas.
    op.execute("DELETE FROM denuncias WHERE encerrada_em IS NOT NULL")
    op.drop_index("uq_denuncia_conta_versao", table_name="denuncias")
    op.create_unique_constraint(
        "uq_denuncia_conta_versao", "denuncias", ["comentario_versao_id", "denunciante_id"]
    )
    op.drop_column("denuncias", "encerrada_em")
    # String vazia nunca verifica como hash válido: rollback não reativa a conta.
    op.execute("UPDATE usuarios SET password_hash = '' WHERE password_hash IS NULL")
    op.alter_column("usuarios", "password_hash", existing_type=sa.String(255), nullable=False)
    # N?o reexpor avalia??es ocultadas ao remover as colunas de estado.
    ids = "SELECT id FROM comentario_versoes WHERE avaliacao_id IN (SELECT id FROM avaliacoes WHERE excluido_em IS NOT NULL)"
    for tabela in ("denuncias", "agradecimentos", "decisoes_moderacao"):
        op.execute(f"DELETE FROM {tabela} WHERE comentario_versao_id IN ({ids})")
    op.execute(f"UPDATE comentario_versoes SET substitui_id=NULL WHERE substitui_id IN ({ids})")
    op.execute(f"DELETE FROM comentario_versoes WHERE id IN ({ids})")
    op.execute("DELETE FROM avaliacoes WHERE excluido_em IS NOT NULL")
    op.drop_column("usuarios", "excluido_em")
    op.drop_index("ix_avaliacoes_purgar_em", table_name="avaliacoes")
    op.drop_column("avaliacoes", "purgar_em")
    op.drop_column("avaliacoes", "excluido_em")
