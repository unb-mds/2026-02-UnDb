"""Representa identidade institucional e turmas com zero ou varios docentes.

Revision ID: 20260917_02
Revises: 20260911_01
Create Date: 2026-09-17
"""

from collections.abc import Sequence
import unicodedata
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "20260917_02"
down_revision: str | Sequence[str] | None = "20260911_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _normalizar(valor: str) -> str:
    decomposed = unicodedata.normalize("NFKD", valor)
    sem_acentos = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(sem_acentos.casefold().split())


def upgrade() -> None:
    op.create_table(
        "unidades",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fonte", sa.String(length=30), nullable=False),
        sa.Column("codigo", sa.String(length=30), nullable=False),
        sa.Column("identificador_externo", sa.String(length=50), nullable=True),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fonte", "codigo", name="uq_unidade_fonte_codigo"),
        sa.UniqueConstraint(
            "fonte",
            "identificador_externo",
            name="uq_unidade_fonte_identificador_externo",
        ),
    )

    op.add_column("professores", sa.Column("nome_normalizado", sa.String(150)))
    op.add_column("professores", sa.Column("siape", sa.String(30), nullable=True))
    op.add_column(
        "professores", sa.Column("identidade_origem", sa.String(255), nullable=True)
    )
    op.add_column(
        "professores",
        sa.Column(
            "identidade_confirmada",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_unique_constraint("uq_professores_siape", "professores", ["siape"])
    op.create_unique_constraint(
        "uq_professores_identidade_origem", "professores", ["identidade_origem"]
    )

    op.add_column(
        "disciplinas", sa.Column("identificador_externo", sa.String(50), nullable=True)
    )
    op.add_column("disciplinas", sa.Column("nome_normalizado", sa.String(150)))

    conexao = op.get_bind()
    for row in conexao.execute(sa.text("SELECT id, nome FROM professores")):
        conexao.execute(
            sa.text(
                "UPDATE professores SET nome_normalizado=:normalizado WHERE id=:id"
            ),
            {"normalizado": _normalizar(row.nome), "id": row.id},
        )
    for row in conexao.execute(sa.text("SELECT id, nome FROM disciplinas")):
        conexao.execute(
            sa.text(
                "UPDATE disciplinas SET nome_normalizado=:normalizado WHERE id=:id"
            ),
            {"normalizado": _normalizar(row.nome), "id": row.id},
        )
    op.alter_column("professores", "nome_normalizado", nullable=False)
    op.alter_column("disciplinas", "nome_normalizado", nullable=False)

    op.add_column("turmas", sa.Column("fonte", sa.String(30)))
    op.add_column("turmas", sa.Column("unidade_id", sa.Uuid()))
    op.add_column("turmas", sa.Column("codigo", sa.String(30)))
    op.add_column(
        "turmas",
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "turmas",
        sa.Column(
            "ultima_observacao_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    unidades: dict[str, object] = {}
    departamentos = conexao.execute(
        sa.text("SELECT DISTINCT departamento FROM disciplinas")
    )
    for row in departamentos:
        unidade_id = uuid4()
        unidades[row.departamento] = unidade_id
        conexao.execute(
            sa.text(
                "INSERT INTO unidades (id, fonte, codigo, nome) "
                "VALUES (:id, 'SIGAA', :codigo, :nome)"
            ),
            {"id": unidade_id, "codigo": row.departamento, "nome": row.departamento},
        )

    turmas_legadas = list(
        conexao.execute(
            sa.text(
                "SELECT t.id, t.professor_id, d.departamento "
                "FROM turmas t JOIN disciplinas d ON d.id=t.disciplina_id"
            )
        )
    )
    for row in turmas_legadas:
        conexao.execute(
            sa.text(
                "UPDATE turmas SET fonte='SIGAA', unidade_id=:unidade_id, "
                "codigo=:codigo WHERE id=:id"
            ),
            {
                "unidade_id": unidades[row.departamento],
                "codigo": f"legacy-{row.id}"[:30],
                "id": row.id,
            },
        )

    op.alter_column("turmas", "fonte", nullable=False)
    op.alter_column("turmas", "unidade_id", nullable=False)
    op.alter_column("turmas", "codigo", nullable=False)
    op.create_foreign_key(
        "fk_turmas_unidade_id", "turmas", "unidades", ["unidade_id"], ["id"]
    )
    op.create_table(
        "turmas_professores",
        sa.Column("turma_id", sa.Uuid(), nullable=False),
        sa.Column("professor_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["turma_id"], ["turmas.id"]),
        sa.ForeignKeyConstraint(["professor_id"], ["professores.id"]),
        sa.PrimaryKeyConstraint("turma_id", "professor_id"),
    )
    for row in turmas_legadas:
        conexao.execute(
            sa.text(
                "INSERT INTO turmas_professores (turma_id, professor_id) "
                "VALUES (:turma_id, :professor_id)"
            ),
            {"turma_id": row.id, "professor_id": row.professor_id},
        )

    op.drop_constraint(
        "uq_turma_disciplina_professor_semestre", "turmas", type_="unique"
    )
    op.drop_constraint("turmas_professor_id_fkey", "turmas", type_="foreignkey")
    op.drop_column("turmas", "professor_id")
    op.create_unique_constraint(
        "uq_turma_identidade_sigaa",
        "turmas",
        ["disciplina_id", "fonte", "unidade_id", "semestre", "codigo"],
    )


def downgrade() -> None:
    conexao = op.get_bind()
    vinculos_incompativeis = conexao.scalar(
        sa.text(
            "SELECT count(*) FROM ("
            "SELECT t.id FROM turmas t "
            "LEFT JOIN turmas_professores tp ON tp.turma_id=t.id "
            "GROUP BY t.id HAVING count(tp.professor_id) <> 1"
            ") AS turmas_incompativeis"
        )
    )
    identidades_legadas_duplicadas = conexao.scalar(
        sa.text(
            "SELECT count(*) FROM ("
            "SELECT t.disciplina_id, tp.professor_id, t.semestre "
            "FROM turmas t "
            "JOIN turmas_professores tp ON tp.turma_id=t.id "
            "GROUP BY t.disciplina_id, tp.professor_id, t.semestre "
            "HAVING count(*) > 1"
            ") AS identidades_duplicadas"
        )
    )
    # O schema anterior representa exatamente um docente por turma e uma unica
    # turma por disciplina/docente/semestre. Recusar a conversao evita inventar
    # docentes, descartar vinculos ou colapsar turmas distintas.
    if vinculos_incompativeis or identidades_legadas_duplicadas:
        raise RuntimeError(
            "downgrade impossivel: os dados atuais nao cabem no modelo anterior de turmas"
        )

    op.add_column("turmas", sa.Column("professor_id", sa.Uuid(), nullable=True))
    conexao.execute(
        sa.text(
            "UPDATE turmas SET professor_id = ("
            "SELECT tp.professor_id FROM turmas_professores tp "
            "WHERE tp.turma_id=turmas.id ORDER BY tp.professor_id LIMIT 1)"
        )
    )
    op.alter_column("turmas", "professor_id", nullable=False)
    op.create_foreign_key(
        "turmas_professor_id_fkey",
        "turmas",
        "professores",
        ["professor_id"],
        ["id"],
    )
    op.drop_constraint("uq_turma_identidade_sigaa", "turmas", type_="unique")
    op.create_unique_constraint(
        "uq_turma_disciplina_professor_semestre",
        "turmas",
        ["disciplina_id", "professor_id", "semestre"],
    )
    op.drop_table("turmas_professores")
    op.drop_constraint("fk_turmas_unidade_id", "turmas", type_="foreignkey")
    op.drop_column("turmas", "ultima_observacao_em")
    op.drop_column("turmas", "ativa")
    op.drop_column("turmas", "codigo")
    op.drop_column("turmas", "unidade_id")
    op.drop_column("turmas", "fonte")

    op.drop_column("disciplinas", "nome_normalizado")
    op.drop_column("disciplinas", "identificador_externo")
    op.drop_constraint("uq_professores_identidade_origem", "professores", type_="unique")
    op.drop_constraint("uq_professores_siape", "professores", type_="unique")
    op.drop_column("professores", "identidade_confirmada")
    op.drop_column("professores", "identidade_origem")
    op.drop_column("professores", "siape")
    op.drop_column("professores", "nome_normalizado")
    op.drop_table("unidades")
