"""Verifica o RF03 com duas transacoes independentes no PostgreSQL.

Este modulo e executado pelo CI depois de ``alembic upgrade head``. Ele fica fora
da descoberta do unittest porque depende de uma instancia PostgreSQL migrada.
"""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.repositories import avaliacao_repository
from app.schemas.avaliacao import AvaliacaoCreate
from app.services import avaliacao_service


def main() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("esta verificacao exige PostgreSQL")

    sufixo = uuid4().hex
    usuario_id = uuid4()
    professor_id = uuid4()
    disciplina_id = uuid4()
    with Session(engine) as db:
        db.add_all(
            (
                Usuario(
                    id=usuario_id,
                    nome="Usuario Concorrente",
                    email=f"concorrencia-{sufixo}@aluno.unb.br",
                    password_hash="hash-de-teste",
                    email_confirmado=True,
                ),
                Professor(
                    id=professor_id,
                    nome="Professor Concorrente",
                    nome_normalizado="professor concorrente",
                    departamento="CIC",
                ),
                Disciplina(
                    id=disciplina_id,
                    codigo=f"T{sufixo[:10]}",
                    nome="Disciplina Concorrente",
                    nome_normalizado="disciplina concorrente",
                    departamento="CIC",
                ),
            )
        )
        db.commit()

    barreira = Barrier(2)
    obter_original = (
        avaliacao_repository.obter_por_avaliador_professor_disciplina
    )

    def obter_sincronizado(*args, **kwargs):  # type: ignore[no-untyped-def]
        avaliacao = obter_original(*args, **kwargs)
        if avaliacao is None:
            barreira.wait(timeout=10)
        return avaliacao

    def registrar(didatica: int) -> tuple[object, int]:
        dados = AvaliacaoCreate(
            professor_id=professor_id,
            disciplina_id=disciplina_id,
            didatica=didatica,
            dificuldade="MEDIO",
            chamada=didatica == 5,
            disponibiliza_material=False,
            qualidade_material=None,
            recomenda=didatica == 5,
        )
        with Session(engine) as db:
            usuario = db.get(Usuario, usuario_id)
            assert usuario is not None
            avaliacao = avaliacao_service.registrar_avaliacao(db, usuario, dados)
            quantidade = db.scalar(select(func.count()).select_from(Avaliacao))
            return avaliacao.id, quantidade

    try:
        with patch.object(
            avaliacao_repository,
            "obter_por_avaliador_professor_disciplina",
            side_effect=obter_sincronizado,
        ):
            with ThreadPoolExecutor(max_workers=2) as executor:
                resultados = list(executor.map(registrar, (1, 5)))

        with Session(engine) as db:
            registros = list(
                db.scalars(
                    select(Avaliacao).where(
                        Avaliacao.usuario_id == usuario_id,
                        Avaliacao.professor_id == professor_id,
                        Avaliacao.disciplina_id == disciplina_id,
                    )
                ).all()
            )

        assert len(registros) == 1
        assert len({resultado[0] for resultado in resultados}) == 1
        assert all(resultado[1] == 1 for resultado in resultados)
        assert registros[0].didatica in {1, 5}
        assert registros[0].updated_at >= registros[0].created_at
    finally:
        with Session(engine) as db:
            db.execute(delete(Avaliacao).where(Avaliacao.usuario_id == usuario_id))
            db.execute(delete(Disciplina).where(Disciplina.id == disciplina_id))
            db.execute(delete(Professor).where(Professor.id == professor_id))
            db.execute(delete(Usuario).where(Usuario.id == usuario_id))
            db.commit()


if __name__ == "__main__":
    main()
