from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
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
    # SQLite continua restrito à suíte determinística; produção usa PostgreSQL.
    inserir = sqlite_insert if db.get_bind().dialect.name == "sqlite" else pg_insert
    respostas = {
        "didatica": didatica,
        "dificuldade": dificuldade,
        "chamada": chamada,
        "disponibiliza_material": disponibiliza_material,
        "qualidade_material": qualidade_material,
        "recomenda": recomenda,
        "updated_at": atualizado_em,
    }
    comando = inserir(Avaliacao).values(
        usuario_id=usuario_id,
        professor_id=professor_id,
        disciplina_id=disciplina_id,
        **respostas,
    )
    # A constraint UNIQUE da migration arbitra também inserções concorrentes.
    # Preserva id/created_at e substitui todos os critérios em uma única escrita.
    comando = comando.on_conflict_do_update(
        index_elements=["usuario_id", "professor_id", "disciplina_id"],
        set_={campo: getattr(comando.excluded, campo) for campo in respostas},
    ).returning(Avaliacao)
    return db.scalars(comando, execution_options={"populate_existing": True}).one()


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
