from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.texto import normalizar_busca
from app.models.disciplina import Disciplina
from app.models.turma import Turma


def get_by_codigo(db: Session, codigo: str) -> Disciplina | None:
    return db.query(Disciplina).filter_by(codigo=codigo).first()


def create(
    db: Session,
    codigo: str,
    nome: str,
    departamento: str,
    identificador_externo: str | None = None,
) -> Disciplina:
    disciplina = Disciplina(
        codigo=codigo,
        identificador_externo=identificador_externo,
        nome=nome,
        nome_normalizado=normalizar_busca(nome),
        departamento=departamento,
    )
    db.add(disciplina)
    db.flush()
    return disciplina


def listar(db: Session, codigo: str | None = None, nome: str | None = None) -> list[Disciplina]:
    consulta = select(Disciplina).order_by(Disciplina.codigo)
    filtros = []
    if codigo is not None:
        filtros.append(Disciplina.codigo.ilike(f"%{codigo.strip()}%"))
    if nome is not None:
        termos = normalizar_busca(nome).split()
        if termos:
            filtros.append(and_(*(Disciplina.nome_normalizado.contains(termo) for termo in termos)))
    if filtros:
        consulta = consulta.where(and_(*filtros))
    return list(db.scalars(consulta).all())


def listar_turmas(db: Session, disciplina_id) -> list[Turma]:
    consulta = (
        select(Turma)
        .options(selectinload(Turma.professores))
        .where(Turma.disciplina_id == disciplina_id, Turma.ativa.is_(True))
        .order_by(Turma.semestre.desc(), Turma.codigo)
    )
    return list(db.scalars(consulta).unique().all())


def listar_mais_avaliadas(db: Session, limite: int = 6):
    from sqlalchemy import func
    from app.models.avaliacao import Avaliacao

    contagens = (
        select(Avaliacao.disciplina_id, func.count(Avaliacao.id).label("total"))
        .group_by(Avaliacao.disciplina_id)
        .subquery()
    )
    consulta = (
        select(Disciplina, contagens.c.total)
        .join(contagens, contagens.c.disciplina_id == Disciplina.id)
        .order_by(contagens.c.total.desc(), Disciplina.nome, Disciplina.id)
        .limit(limite)
    )
    return list(db.execute(consulta).all())
