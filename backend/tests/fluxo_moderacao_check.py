"""Check final invariants of fluxo-moderacao-browser against its synthetic fixture.

Use only PostgreSQL disposable tests: python -m tests.fluxo_moderacao_check < fixture.json
"""

import json
import os
import sys
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models import Agradecimento, Avaliacao, ComentarioVersao, DecisaoModeracao, Denuncia


def main():
    if os.environ.get("UNDB_INTEGRATION_TEST") != "1" or engine.dialect.name != "postgresql":
        raise RuntimeError("Exige UNDB_INTEGRATION_TEST=1 e PostgreSQL descartavel")
    fixture = json.load(sys.stdin)
    with Session(engine) as db:
        avaliacoes = list(
            db.scalars(
                select(Avaliacao).where(
                    Avaliacao.professor_id == UUID(fixture["professorId"]),
                    Avaliacao.disciplina_id == UUID(fixture["disciplinaId"]),
                    Avaliacao.usuario.has(email=fixture["outraConta"]["email"]),
                )
            )
        )
        assert len(avaliacoes) == 1, "deve existir somente uma avaliacao"
        avaliacao = avaliacoes[0]
        assert (
            avaliacao.didatica,
            avaliacao.dificuldade.value,
            avaliacao.chamada,
            avaliacao.disponibiliza_material,
            avaliacao.qualidade_material.value,
            avaliacao.recomenda,
        ) == (4, "MEDIO", True, True, "BOM", True)
        versoes = list(
            db.scalars(
                select(ComentarioVersao).where(ComentarioVersao.avaliacao_id == avaliacao.id)
            )
        )
        ids = [v.id for v in versoes]
        assert not any(v.estado.value in ("PUBLICADO", "PENDENTE", "SUSPENSO") for v in versoes)
        assert any(v.estado.value == "RETIRADO" for v in versoes)
        assert all(v.texto is None for v in versoes if v.estado.value == "SUBSTITUIDO")
        assert (
            db.scalar(select(func.count(Denuncia.id)).where(Denuncia.comentario_versao_id.in_(ids)))
            == 0
        )
        assert (
            db.scalar(
                select(func.count(Agradecimento.id)).where(
                    Agradecimento.comentario_versao_id.in_(ids)
                )
            )
            == 0
        )
        decisoes = list(
            db.scalars(
                select(DecisaoModeracao).where(DecisaoModeracao.comentario_versao_id.in_(ids))
            )
        )
        assert {d.acao for d in decisoes} >= {"APROVAR", "MANTER", "REMOVER"}
        assert all(
            d.motivo
            and d.moderador_id
            and d.created_at
            and d.estado_anterior
            and d.estado_posterior
            for d in decisoes
        )
    print(
        "Issue163 PostgreSQL: avaliacao unica, criterios preservados, nenhuma versao ativa/denuncia/agradecimento pendente; decisoes com motivo, ator, data e transicao."
    )


if __name__ == "__main__":
    main()
