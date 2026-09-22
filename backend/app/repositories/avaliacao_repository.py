from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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


def _substituir_criterios(
    avaliacao: Avaliacao,
    *,
    didatica: int,
    dificuldade: Dificuldade,
    chamada: bool,
    disponibiliza_material: bool,
    qualidade_material: QualidadeMaterial | None,
    recomenda: bool,
) -> None:
    avaliacao.didatica = didatica
    avaliacao.dificuldade = dificuldade
    avaliacao.chamada = chamada
    avaliacao.disponibiliza_material = disponibiliza_material
    avaliacao.qualidade_material = qualidade_material
    avaliacao.recomenda = recomenda
    avaliacao.updated_at = datetime.now(timezone.utc)


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
) -> Avaliacao:
    avaliacao = obter_por_avaliador_professor_disciplina(
        db,
        usuario_id,
        professor_id,
        disciplina_id,
    )
    if avaliacao is None:
        nova_avaliacao = Avaliacao(
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
        try:
            # A constraint pode perder a corrida depois da leitura inicial. O
            # savepoint desfaz apenas o INSERT e preserva a sessao para atualizar
            # a linha que venceu, sem rollback da transacao externa.
            with db.begin_nested():
                db.add(nova_avaliacao)
                db.flush()
            return nova_avaliacao
        except IntegrityError:
            avaliacao = obter_por_avaliador_professor_disciplina(
                db,
                usuario_id,
                professor_id,
                disciplina_id,
            )
            if avaliacao is None:
                raise

    _substituir_criterios(
        avaliacao,
        didatica=didatica,
        dificuldade=dificuldade,
        chamada=chamada,
        disponibiliza_material=disponibiliza_material,
        qualidade_material=qualidade_material,
        recomenda=recomenda,
    )
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
