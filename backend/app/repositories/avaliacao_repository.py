from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, joinedload

from app.domain.avaliacoes import ContagensAvaliacoes
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade, QualidadeMaterial
from app.models.professor import Professor
from app.repositories.reconciliacao_professor_repository import resolver_id


def obter_professor(db: Session, professor_id: UUID) -> Professor | None:
    return db.get(Professor, resolver_id(db, professor_id))


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
        Avaliacao.excluido_em.is_(None),
    )
    return list(db.scalars(consulta).all())


def listar_do_usuario(
    db: Session, usuario_id: UUID, pagina: int, tamanho: int = 10
) -> tuple[list[Avaliacao], int]:
    filtros = (Avaliacao.usuario_id == usuario_id, Avaliacao.excluido_em.is_(None))
    total = db.scalar(select(func.count(Avaliacao.id)).where(*filtros)) or 0
    consulta = (
        select(Avaliacao)
        .where(*filtros)
        .options(joinedload(Avaliacao.professor), joinedload(Avaliacao.disciplina))
        .order_by(Avaliacao.updated_at.desc(), Avaliacao.id)
        .offset((pagina - 1) * tamanho)
        .limit(tamanho)
    )
    return list(db.scalars(consulta).all()), total


def contar_por_disciplina_e_professores(
    db: Session,
    disciplina_id: UUID,
    professor_ids: list[UUID],
) -> dict[UUID, ContagensAvaliacoes]:
    if not professor_ids:
        return {}

    tem_material = Avaliacao.disponibiliza_material.is_(True)
    consulta = (
        select(
            Avaliacao.professor_id,
            func.count().label("total"),
            func.sum(Avaliacao.didatica).label("soma_didatica"),
            func.count().filter(Avaliacao.chamada.is_(True)).label("chamadas"),
            func.count().filter(tem_material).label("materiais"),
            func.count().filter(Avaliacao.recomenda.is_(True)).label("recomendacoes"),
            *(
                func.count().filter(Avaliacao.dificuldade == valor)
                for valor in (Dificuldade.FACIL, Dificuldade.MEDIO, Dificuldade.DIFICIL)
            ),
            *(
                func.count().filter(tem_material, Avaliacao.qualidade_material == valor)
                for valor in (
                    QualidadeMaterial.RUIM,
                    QualidadeMaterial.MEDIO,
                    QualidadeMaterial.BOM,
                )
            ),
        )
        .where(
            Avaliacao.disciplina_id == disciplina_id,
            Avaliacao.professor_id.in_(professor_ids),
            Avaliacao.excluido_em.is_(None),
        )
        .group_by(Avaliacao.professor_id)
    )
    return {
        professor_id: ContagensAvaliacoes(
            total=total,
            soma_didatica=soma_didatica,
            dificuldades=(facil, medio, dificil),
            chamadas=chamadas,
            materiais=materiais,
            qualidades=(ruim, regular, bom),
            recomendacoes=recomendacoes,
        )
        for (
            professor_id,
            total,
            soma_didatica,
            chamadas,
            materiais,
            recomendacoes,
            facil,
            medio,
            dificil,
            ruim,
            regular,
            bom,
        ) in db.execute(consulta)
    }
