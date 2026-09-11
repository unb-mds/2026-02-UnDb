"""Create the initial schema defined in specs.md.

Revision ID: 20260911_01
Revises:
Create Date: 2026-09-11
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260911_01"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

dificuldade = sa.Enum("FACIL", "MEDIO", "DIFICIL", name="dificuldade")
qualidade_material = sa.Enum("RUIM", "MEDIO", "BOM", name="qualidade_material")


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("email_confirmado", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "professores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("departamento", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "disciplinas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("codigo", sa.String(length=20), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("departamento", sa.String(length=100), nullable=False),
        sa.Column("creditos", sa.SmallInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )
    op.create_table(
        "turmas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("disciplina_id", sa.Uuid(), nullable=False),
        sa.Column("professor_id", sa.Uuid(), nullable=False),
        sa.Column("semestre", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["disciplina_id"], ["disciplinas.id"]),
        sa.ForeignKeyConstraint(["professor_id"], ["professores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "disciplina_id",
            "professor_id",
            "semestre",
            name="uq_turma_disciplina_professor_semestre",
        ),
    )

    op.create_table(
        "avaliacoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("professor_id", sa.Uuid(), nullable=False),
        sa.Column("disciplina_id", sa.Uuid(), nullable=False),
        sa.Column("didatica", sa.SmallInteger(), nullable=False),
        sa.Column("dificuldade", dificuldade, nullable=False),
        sa.Column("chamada", sa.Boolean(), nullable=False),
        sa.Column("disponibiliza_material", sa.Boolean(), nullable=False),
        sa.Column("qualidade_material", qualidade_material, nullable=True),
        sa.Column("recomenda", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("didatica BETWEEN 1 AND 5", name="ck_avaliacao_didatica"),
        sa.CheckConstraint(
            "(disponibiliza_material AND qualidade_material IS NOT NULL) OR "
            "(NOT disponibiliza_material AND qualidade_material IS NULL)",
            name="ck_avaliacao_qualidade_material",
        ),
        sa.ForeignKeyConstraint(["disciplina_id"], ["disciplinas.id"]),
        sa.ForeignKeyConstraint(["professor_id"], ["professores.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "usuario_id",
            "professor_id",
            "disciplina_id",
            name="uq_avaliacao_usuario_professor_disciplina",
        ),
    )


def downgrade() -> None:
    op.drop_table("avaliacoes")
    op.drop_table("turmas")
    op.drop_table("disciplinas")
    op.drop_table("professores")
    op.drop_table("usuarios")
    qualidade_material.drop(op.get_bind(), checkfirst=True)
    dificuldade.drop(op.get_bind(), checkfirst=True)
