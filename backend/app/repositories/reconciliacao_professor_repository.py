from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, insert, select, text, update
from sqlalchemy.orm import Session

from app.models.avaliacao import Avaliacao
from app.models.professor import Professor
from app.models.professor_correspondencia import ProfessorCorrespondencia
from app.models.turma import turmas_professores


class ReconciliacaoRecusada(ValueError):
    pass


def resolver_id(db: Session, professor_id: UUID) -> UUID:
    destino = db.scalar(
        select(ProfessorCorrespondencia.destino_id).where(
            ProfessorCorrespondencia.origem_id == professor_id
        )
    )
    return destino if destino is not None else professor_id


def planejar(db: Session, origem_id: UUID, destino_id: UUID) -> dict:
    if origem_id == destino_id:
        raise ReconciliacaoRecusada("Origem e destino devem ser distintos.")
    origem = db.get(Professor, origem_id)
    destino = db.get(Professor, destino_id)
    if origem is None or destino is None:
        raise ReconciliacaoRecusada("Professor não encontrado.")
    anterior = db.get(ProfessorCorrespondencia, origem_id)
    if anterior is not None:
        if anterior.destino_id != destino_id:
            raise ReconciliacaoRecusada("A origem já aponta para outro destino.")
        return {"estado": "ja_aplicada", "origem": str(origem_id), "destino": str(destino_id)}
    if (
        resolver_id(db, destino_id) != destino_id
        or db.scalar(
            select(ProfessorCorrespondencia.origem_id)
            .where(ProfessorCorrespondencia.destino_id == origem_id)
            .limit(1)
        )
        is not None
    ):
        raise ReconciliacaoRecusada(
            "Cadeias e ciclos não são permitidos; escolher o destino final."
        )
    if origem.siape or origem.identidade_confirmada or not origem.identidade_origem:
        raise ReconciliacaoRecusada("A origem deve ser uma ocorrência provisória sem SIAPE.")
    colisoes = db.execute(
        select(Avaliacao.usuario_id, Avaliacao.disciplina_id)
        .where(Avaliacao.professor_id.in_([origem_id, destino_id]))
        .group_by(Avaliacao.usuario_id, Avaliacao.disciplina_id)
        .having(func.count() > 1)
    ).all()
    turmas = list(
        db.scalars(
            select(turmas_professores.c.turma_id).where(
                turmas_professores.c.professor_id == origem_id
            )
        )
    )
    total = db.scalar(
        select(func.count()).select_from(Avaliacao).where(Avaliacao.professor_id == origem_id)
    )
    return {
        "estado": "bloqueada" if colisoes else "pronta_para_confirmacao",
        "origem": str(origem_id),
        "destino": str(destino_id),
        "nome_origem": origem.nome,
        "nome_destino": destino.nome,
        "identidade_origem": origem.identidade_origem,
        "turmas": len(turmas),
        "avaliacoes": total,
        "colisoes": len(colisoes),
    }


def _bloquear_escritas(db: Session) -> None:
    # A operação é de manutenção. Bloqueia importações/escritas concorrentes no
    # PostgreSQL antes de verificar colisões; não depende só de uma prévia antiga.
    if db.bind.dialect.name == "postgresql":
        db.execute(text("SET LOCAL lock_timeout = '5s'"))
        db.execute(
            text(
                "LOCK TABLE professores, turmas_professores, avaliacoes, "
                "professor_correspondencias IN SHARE ROW EXCLUSIVE MODE"
            )
        )


def planejar_grupo(db: Session, origem_ids: Sequence[UUID], destino_id: UUID) -> dict:
    if not origem_ids or len(set(origem_ids)) != len(origem_ids):
        raise ReconciliacaoRecusada("Informar ao menos uma origem, sem IDs repetidos.")
    planos = [planejar(db, origem_id, destino_id) for origem_id in origem_ids]
    # Verificar o conjunto também detecta avaliações conflitantes entre duas
    # origens, mesmo quando nenhuma delas conflita com o destino inicialmente.
    colisoes = db.execute(
        select(Avaliacao.usuario_id, Avaliacao.disciplina_id)
        .where(Avaliacao.professor_id.in_([*origem_ids, destino_id]))
        .group_by(Avaliacao.usuario_id, Avaliacao.disciplina_id)
        .having(func.count() > 1)
    ).all()
    estado = "pronta_para_confirmacao"
    if colisoes:
        estado = "bloqueada"
    elif all(plano["estado"] == "ja_aplicada" for plano in planos):
        estado = "ja_aplicada"
    return {
        "estado": estado,
        "destino": str(destino_id),
        "correspondencias": planos,
        "colisoes": len(colisoes),
    }


def aplicar_grupo(
    db: Session, origem_ids: Sequence[UUID], destino_id: UUID, evidencia: str
) -> dict:
    _bloquear_escritas(db)
    plano = planejar_grupo(db, origem_ids, destino_id)
    if plano["estado"] == "ja_aplicada":
        return plano
    if plano["colisoes"]:
        raise ReconciliacaoRecusada("Colisão de avaliações: nada foi unido ou descartado.")
    with db.begin_nested():
        resultados = [aplicar(db, origem_id, destino_id, evidencia) for origem_id in origem_ids]
    return plano | {"estado": "aplicada", "correspondencias": resultados}


def aplicar(db: Session, origem_id: UUID, destino_id: UUID, evidencia: str) -> dict:
    evidencia = evidencia.strip()
    if not 1 <= len(evidencia) <= 500:
        raise ReconciliacaoRecusada("Registrar evidência de 1 a 500 caracteres.")
    _bloquear_escritas(db)
    plano = planejar(db, origem_id, destino_id)
    if plano["estado"] == "ja_aplicada":
        return plano
    if plano["colisoes"]:
        raise ReconciliacaoRecusada("Colisão de avaliações: nada foi unido ou descartado.")
    with db.begin_nested():
        origem_turmas = set(
            db.scalars(
                select(turmas_professores.c.turma_id).where(
                    turmas_professores.c.professor_id == origem_id
                )
            )
        )
        destino_turmas = set(
            db.scalars(
                select(turmas_professores.c.turma_id).where(
                    turmas_professores.c.professor_id == destino_id
                )
            )
        )
        for turma_id in origem_turmas - destino_turmas:
            db.execute(
                insert(turmas_professores).values(turma_id=turma_id, professor_id=destino_id)
            )
        db.execute(delete(turmas_professores).where(turmas_professores.c.professor_id == origem_id))
        # Mantém IDs, textos, versões, denúncias e decisões: só muda a FK do professor.
        db.execute(
            update(Avaliacao)
            .where(Avaliacao.professor_id == origem_id)
            .values(professor_id=destino_id, updated_at=Avaliacao.updated_at)
        )
        db.add(
            ProfessorCorrespondencia(
                origem_id=origem_id, destino_id=destino_id, evidencia=evidencia
            )
        )
        db.flush()
    return plano | {"estado": "aplicada"}


def validar_grupo_em_lote(db, origem_ids, destino_id, evidencia):
    """Mesmas barreiras de integridade, consultas por conjunto em vez de por origem."""
    from app.models.identidade_docente import IdentidadeDocente

    evidencia = evidencia.strip()
    origens = set(origem_ids)
    if not evidencia or len(evidencia) > 500 or not origens or destino_id in origens:
        raise ReconciliacaoRecusada("Origens distintas do destino e evidência são obrigatórias.")
    todos = origens | {destino_id}
    docentes = {p.id: p for p in db.scalars(select(Professor).where(Professor.id.in_(todos)))}
    if set(docentes) != todos:
        raise ReconciliacaoRecusada("Professor não encontrado.")
    correspondencias = list(
        db.scalars(
            select(ProfessorCorrespondencia).where(
                ProfessorCorrespondencia.origem_id.in_(todos)
                | ProfessorCorrespondencia.destino_id.in_(origens)
            )
        )
    )
    if any(c.origem_id in todos for c in correspondencias):
        raise ReconciliacaoRecusada(
            "Cadeias, ciclos ou correspondências prévias: escolher o destino final."
        )
    if any(
        p.siape or p.identidade_confirmada or not p.identidade_origem
        for id, p in docentes.items()
        if id in origens
    ):
        raise ReconciliacaoRecusada("A origem deve ser provisória sem SIAPE.")
    institucionais = list(
        db.scalars(select(IdentidadeDocente).where(IdentidadeDocente.professor_id.in_(todos)))
    )
    if len(institucionais) > 1 or any(i.professor_id in origens for i in institucionais):
        raise ReconciliacaoRecusada("Preservar a identidade institucional no destino.")
    colisao = db.execute(
        select(Avaliacao.usuario_id, Avaliacao.disciplina_id)
        .where(Avaliacao.professor_id.in_(todos))
        .group_by(Avaliacao.usuario_id, Avaliacao.disciplina_id)
        .having(func.count() > 1)
        .limit(1)
    ).first()
    if colisao:
        raise ReconciliacaoRecusada("Colisão de avaliações: nada foi unido ou descartado.")


def aplicar_grupo_em_lote(db, origem_ids, destino_id, evidencia):
    """Executa o plano validado sob lock; caller mantém savepoint por grupo."""
    from app.models.identidade_docente import IdentidadeLocal

    _bloquear_escritas(db)
    validar_grupo_em_lote(db, origem_ids, destino_id, evidencia)
    origens = set(origem_ids)
    evidencia = evidencia.strip()
    # INSERT SELECT evita consultas e INSERTs individuais por vínculo de turma.
    origem_turmas = (
        select(turmas_professores.c.turma_id)
        .where(turmas_professores.c.professor_id.in_(origens))
        .distinct()
    )
    destino_turmas = select(turmas_professores.c.turma_id).where(
        turmas_professores.c.professor_id == destino_id
    )
    from sqlalchemy import literal

    origem_turmas = origem_turmas.subquery()
    db.execute(
        insert(turmas_professores).from_select(
            ["turma_id", "professor_id"],
            select(origem_turmas.c.turma_id, literal(destino_id, type_=Professor.id.type)).where(
                ~origem_turmas.c.turma_id.in_(destino_turmas)
            ),
        )
    )
    db.execute(delete(turmas_professores).where(turmas_professores.c.professor_id.in_(origens)))
    db.execute(
        update(Avaliacao)
        .where(Avaliacao.professor_id.in_(origens))
        .values(professor_id=destino_id, updated_at=Avaliacao.updated_at)
    )
    db.execute(
        update(IdentidadeLocal)
        .where(IdentidadeLocal.professor_id.in_(origens))
        .values(professor_id=destino_id)
    )
    # Se um cadastro local já consolidado recebe perfil de outro UUID, achatar os
    # aliases anteriores preserva todos os links antigos sem criar cadeias.
    db.execute(
        update(ProfessorCorrespondencia)
        .where(ProfessorCorrespondencia.destino_id.in_(origens))
        .values(destino_id=destino_id)
    )
    db.execute(
        insert(ProfessorCorrespondencia),
        [
            {"origem_id": id, "destino_id": destino_id, "evidencia": evidencia}
            for id in sorted(origens, key=str)
        ],
    )
    db.flush()
