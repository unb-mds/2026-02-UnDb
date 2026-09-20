"""Verifica preservacao de dados ao migrar o schema institucional.

Este modulo e executado pelo CI somente contra o PostgreSQL descartavel do job.
Ele nao integra a descoberta do unittest porque depende de uma revisao Alembic
especifica ja aplicada ao banco.
"""

import argparse
from uuid import UUID

from sqlalchemy import text

from app.core.database import engine


USUARIO_ID = UUID("00000000-0000-0000-0000-000000000001")
PROFESSOR_ID = UUID("00000000-0000-0000-0000-000000000002")
DISCIPLINA_ID = UUID("00000000-0000-0000-0000-000000000003")
TURMA_ID = UUID("00000000-0000-0000-0000-000000000004")
AVALIACAO_ID = UUID("00000000-0000-0000-0000-000000000005")


def _scalar(sql: str, **parametros):  # type: ignore[no-untyped-def]
    with engine.connect() as conexao:
        return conexao.scalar(text(sql), parametros)


def seed() -> None:
    with engine.begin() as conexao:
        conexao.execute(
            text(
                "INSERT INTO usuarios "
                "(id, nome, email, password_hash, email_confirmado) "
                "VALUES (:id, 'Usuario Legado', 'legado@aluno.unb.br', "
                "'hash-legado', true)"
            ),
            {"id": USUARIO_ID},
        )
        conexao.execute(
            text(
                "INSERT INTO professores (id, nome, departamento) "
                "VALUES (:id, 'PROFESSORA TÉSTE', 'CIC')"
            ),
            {"id": PROFESSOR_ID},
        )
        conexao.execute(
            text(
                "INSERT INTO disciplinas (id, codigo, nome, departamento) "
                "VALUES (:id, 'CIC0002', "
                "'FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO', 'CIC')"
            ),
            {"id": DISCIPLINA_ID},
        )
        conexao.execute(
            text(
                "INSERT INTO turmas "
                "(id, disciplina_id, professor_id, semestre) "
                "VALUES (:id, :disciplina_id, :professor_id, '2026.2')"
            ),
            {
                "id": TURMA_ID,
                "disciplina_id": DISCIPLINA_ID,
                "professor_id": PROFESSOR_ID,
            },
        )
        conexao.execute(
            text(
                "INSERT INTO avaliacoes "
                "(id, usuario_id, professor_id, disciplina_id, didatica, "
                "dificuldade, chamada, disponibiliza_material, "
                "qualidade_material, recomenda) "
                "VALUES (:id, :usuario_id, :professor_id, :disciplina_id, 5, "
                "'MEDIO', true, true, 'BOM', true)"
            ),
            {
                "id": AVALIACAO_ID,
                "usuario_id": USUARIO_ID,
                "professor_id": PROFESSOR_ID,
                "disciplina_id": DISCIPLINA_ID,
            },
        )


def verify_upgrade() -> None:
    assert _scalar("SELECT count(*) FROM usuarios WHERE id=:id", id=USUARIO_ID) == 1
    assert _scalar(
        "SELECT count(*) FROM avaliacoes WHERE id=:id", id=AVALIACAO_ID
    ) == 1
    assert _scalar(
        "SELECT nome_normalizado FROM professores WHERE id=:id", id=PROFESSOR_ID
    ) == "professora teste"
    assert _scalar(
        "SELECT nome_normalizado FROM disciplinas WHERE id=:id", id=DISCIPLINA_ID
    ) == "fundamentos teoricos da computacao"
    assert _scalar(
        "SELECT count(*) FROM turmas_professores "
        "WHERE turma_id=:turma_id AND professor_id=:professor_id",
        turma_id=TURMA_ID,
        professor_id=PROFESSOR_ID,
    ) == 1
    assert _scalar(
        "SELECT count(*) FROM turmas t "
        "JOIN unidades u ON u.id=t.unidade_id "
        "WHERE t.id=:id AND t.fonte='SIGAA' AND t.codigo IS NOT NULL "
        "AND t.ativa=true AND u.codigo='CIC'",
        id=TURMA_ID,
    ) == 1


def verify_downgrade() -> None:
    assert _scalar("SELECT count(*) FROM usuarios WHERE id=:id", id=USUARIO_ID) == 1
    assert _scalar(
        "SELECT count(*) FROM avaliacoes WHERE id=:id", id=AVALIACAO_ID
    ) == 1
    assert _scalar(
        "SELECT count(*) FROM turmas "
        "WHERE id=:id AND professor_id=:professor_id",
        id=TURMA_ID,
        professor_id=PROFESSOR_ID,
    ) == 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "acao",
        choices=("seed", "verify-upgrade", "verify-downgrade"),
    )
    args = parser.parse_args()
    {
        "seed": seed,
        "verify-upgrade": verify_upgrade,
        "verify-downgrade": verify_downgrade,
    }[args.acao]()


if __name__ == "__main__":
    main()
