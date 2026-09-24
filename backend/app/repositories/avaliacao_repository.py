from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade, QualidadeMaterial
from app.models.professor import Professor


def obter_professor(db: Session, professor_id: UUID) -> Professor | None:
    return db.get(Professor, professor_id)


def obter_disciplina(db: Session, disciplina_id: UUID) -> Disciplina | None:
    return db.get(Disciplina, disciplina_id)


def obter_por_avaliador_professor_disciplina(
    db: Session,
    usuario_id: UUID,
    professor_id: UUID,
    disciplina_id: UUID,
) -> Avaliacao | None:
    consulta = select(Avaliacao).where(
        Avaliacao.usuario_id == usuario_id,
        Avaliacao.professor_id == professor_id,
        Avaliacao.disciplina_id == disciplina_id,
    )
    return db.scalar(consulta)


def salvar_ou_substituir(
    db: Session,
    *,
    usuario_id: UUID,
    professor_id: UUID,
    disciplina_id: UUID,
    didatica: int,
    dificuldade: Dificuldade,
    chamada: bool,
    disponibiliza_material: bool,
    qualidade_material: QualidadeMaterial | None,
    recomenda: bool,
    atualizado_em: datetime,
) -> Avaliacao:
    avaliacao = obter_por_avaliador_professor_disciplina(
        db,
        usuario_id,
        professor_id,
        disciplina_id,
    )
    if avaliacao is None:
        avaliacao = Avaliacao(
            usuario_id=usuario_id,
            professor_id=professor_id,
            disciplina_id=disciplina_id,
            didatica=didatica,
            dificuldade=dificuldade,
            chamada=chamada,
            disponibiliza_material=disponibiliza_material,
            qualidade_material=qualidade_material,
            recomenda=recomenda,
        )
        db.add(avaliacao)
        return avaliacao

    avaliacao.didatica = didatica
    avaliacao.dificuldade = dificuldade
    avaliacao.chamada = chamada
    avaliacao.disponibiliza_material = disponibiliza_material
    avaliacao.qualidade_material = qualidade_material
    avaliacao.recomenda = recomenda
    avaliacao.updated_at = atualizado_em
    return avaliacao


def listar_por_professor_e_disciplina(
    db: Session,
    professor_id: UUID,
    disciplina_id: UUID,
) -> list[Avaliacao]:
    consulta = select(Avaliacao).where(
        Avaliacao.professor_id == professor_id,
        Avaliacao.disciplina_id == disciplina_id,
    )
    return list(db.scalars(consulta).all())
