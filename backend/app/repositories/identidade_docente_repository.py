"""Persistência e serialização de identidades; não altera avaliações na API."""

from sqlalchemy import select, text
from app.models.identidade_docente import IdentidadeDocente, PendenciaIdentidade, DecisaoIdentidade
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.repositories.reconciliacao_professor_repository import resolver_id


def bloquear(db):
    if db.bind.dialect.name == "postgresql":
        # Mesmo limite da reconciliação: importações consultam rede enquanto
        # mantêm este lock, portanto uma decisão não pode esperar sem limite.
        db.execute(text("SET LOCAL lock_timeout = '5s'"))
        db.execute(text("SELECT pg_advisory_xact_lock(2071101)"))


def obter(db, chave):
    return db.scalar(select(PendenciaIdentidade).where(PendenciaIdentidade.chave == chave))


def por_id(db, id):
    return db.get(PendenciaIdentidade, id, populate_existing=True)


def professor(db, id):
    return db.get(Professor, resolver_id(db, id))


def identidade(db, identificador):
    return db.get(IdentidadeDocente, identificador)


def vincular(db, identificador, docente):
    if docente.siape and docente.siape != identificador:
        raise ValueError("SIAPE existente diverge do identificador apresentado.")
    outra = identidade_do_professor(db, docente.id)
    if outra and outra.identificador != identificador:
        raise ValueError("A origem já possui outra identidade institucional.")
    atual = identidade(db, identificador)
    if atual:
        return professor(db, atual.professor_id)
    if outra:
        raise ValueError("O professor já possui outro identificador institucional.")
    db.add(
        IdentidadeDocente(identificador=identificador, professor_id=docente.id, nome=docente.nome)
    )
    db.flush()
    return docente


def listar(db, estado, limite=50, offset=0):
    return list(
        db.scalars(
            select(PendenciaIdentidade)
            .where(PendenciaIdentidade.estado == estado)
            .order_by(PendenciaIdentidade.created_at, PendenciaIdentidade.id)
            .limit(limite)
            .offset(offset)
        )
    )


def confirmadas(db):
    return list(
        db.scalars(
            select(PendenciaIdentidade)
            .where(PendenciaIdentidade.estado == "CONFIRMADA")
            .order_by(PendenciaIdentidade.identificador_destino, PendenciaIdentidade.chave)
        )
    )


def decisoes(db, id):
    return list(
        db.scalars(
            select(DecisaoIdentidade)
            .where(DecisaoIdentidade.pendencia_id == id)
            .order_by(DecisaoIdentidade.created_at, DecisaoIdentidade.id)
        )
    )


def conceder(db, email, valor):
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    if usuario is None or not usuario.email_confirmado:
        raise ValueError("Conta confirmada não encontrada.")
    usuario.reconciliador = valor


def identidade_do_professor(db, id):
    return db.scalar(select(IdentidadeDocente).where(IdentidadeDocente.professor_id == id))
