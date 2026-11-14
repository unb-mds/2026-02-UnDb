"""Persistência e serialização de identidades; não altera avaliações na API."""

from sqlalchemy import select, text
from app.models.identidade_docente import IdentidadeDocente, PendenciaIdentidade, DecisaoIdentidade
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.repositories.reconciliacao_professor_repository import resolver_id

MOTIVOS_FALLBACK_LOCAL = ("PERFIL_AUSENTE", "DISCIPLINA_NAO_CONFIRMADA")
MOTIVOS_REVISAO_LOCAL = ("HOMONIMOS", "CONSULTA_INCONCLUSIVA")
MOTIVOS_ASSOCIACAO_LOCAL = ("ASSOCIACAO_LOCAL", "ASSOCIACAO_LOCAL_REVISADA")


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


def local(db, nome, unidade):
    from app.domain.texto import normalizar_busca
    from app.models.identidade_docente import IdentidadeLocal

    return db.get(IdentidadeLocal, (normalizar_busca(nome), unidade))


def vincular_local(db, nome, unidade, docente):
    from app.domain.texto import normalizar_busca
    from app.models.identidade_docente import IdentidadeLocal

    atual = local(db, nome, unidade)
    if atual is None:
        atual = IdentidadeLocal(
            nome_normalizado=normalizar_busca(nome), unidade=unidade, professor_id=docente.id
        )
        db.add(atual)
        db.flush()
    return professor(db, atual.professor_id)


def separacao_humana(db, nome, unidade):
    from app.domain.texto import normalizar_busca

    # Decisões de manter separados não podem ser contornadas por uma nova turma.
    return any(
        normalizar_busca(n) == normalizar_busca(nome)
        for n in db.scalars(
            select(PendenciaIdentidade.nome).where(
                PendenciaIdentidade.unidade == unidade,
                PendenciaIdentidade.humana.is_(True),
                PendenciaIdentidade.estado == "SEPARADA",
            )
        )
    )


def grupos_locais(db, incluir_revisadas=False):
    """Snapshot escalar; não manter milhares de ORM expirados entre commits."""
    from collections import defaultdict
    from app.domain.texto import normalizar_busca

    grupos = defaultdict(list)
    for item in db.scalars(
        select(PendenciaIdentidade)
        .where(
            PendenciaIdentidade.humana.is_(False),
            PendenciaIdentidade.estado == "PENDENTE",
            PendenciaIdentidade.motivo.in_(
                MOTIVOS_FALLBACK_LOCAL + (MOTIVOS_REVISAO_LOCAL if incluir_revisadas else ())
            ),
        )
        .order_by(PendenciaIdentidade.chave)
    ):
        grupos[(normalizar_busca(item.nome), item.unidade)].append(item.id)
    return grupos


def itens_por_ids(db, ids):
    return list(db.scalars(select(PendenciaIdentidade).where(PendenciaIdentidade.id.in_(ids))))


def grupos_confirmados(db):
    from collections import defaultdict

    grupos = defaultdict(list)
    for identificador, id in db.execute(
        select(PendenciaIdentidade.identificador_destino, PendenciaIdentidade.id)
        .where(PendenciaIdentidade.estado == "CONFIRMADA")
        .order_by(PendenciaIdentidade.identificador_destino, PendenciaIdentidade.chave)
    ):
        grupos[identificador].append(id)
    return grupos


def professores_canonicos(db, ids):
    from app.models.professor_correspondencia import ProfessorCorrespondencia

    destinos = dict(
        db.execute(
            select(ProfessorCorrespondencia.origem_id, ProfessorCorrespondencia.destino_id).where(
                ProfessorCorrespondencia.origem_id.in_(ids)
            )
        ).all()
    )
    finais = {destinos.get(id, id) for id in ids}
    return list(db.scalars(select(Professor).where(Professor.id.in_(finais))))


def vincular_grupo(db, identificador, ids):
    docentes = professores_canonicos(db, ids)
    atuais = list(
        db.scalars(
            select(IdentidadeDocente).where(
                IdentidadeDocente.professor_id.in_([p.id for p in docentes])
            )
        )
    )
    if any(p.siape and p.siape != identificador for p in docentes) or any(
        i.identificador != identificador for i in atuais
    ):
        raise ValueError("Grupo possui outra identidade institucional.")
    atual = identidade(db, identificador)
    destino = professor(db, atual.professor_id) if atual else docentes[0]
    if atual is None:
        db.add(
            IdentidadeDocente(
                identificador=identificador, professor_id=destino.id, nome=destino.nome
            )
        )
        db.flush()
    return destino, {p.id for p in docentes} - {destino.id}


def destino_local_grupo(db, nome, unidade, ids):
    conhecidos = perfis_conhecidos(db, nome, unidade)
    if len(conhecidos) > 1:
        raise ValueError("Mais de uma identidade institucional conhecida nesta unidade.")
    if separacao_humana(db, nome, unidade):
        raise ValueError("Há decisão humana de manter separados nesta unidade.")
    associacao = local(db, nome, unidade)
    # A identidade institucional já conhecida deve ser o destino, inclusive
    # quando não aparece entre as ocorrências provisórias deste lote.
    extras = [associacao.professor_id] if associacao else []
    if conhecidos:
        extras.append(identidade(db, conhecidos[0]).professor_id)
    docentes = professores_canonicos(db, ids + extras)
    institucionais = list(
        db.scalars(
            select(IdentidadeDocente).where(
                IdentidadeDocente.professor_id.in_([p.id for p in docentes])
            )
        )
    )
    if len(institucionais) > 1:
        raise ValueError("Mais de uma identidade institucional: revisar o grupo.")
    # Preservar UUID institucional ou o local já usado antes de escolher uma origem.
    destino = (
        professor(db, institucionais[0].professor_id)
        if institucionais
        else professor(db, associacao.professor_id)
        if associacao
        else sorted(docentes, key=lambda p: str(p.id))[0]
    )
    return destino, {p.id for p in docentes} - {destino.id}


def perfis_conhecidos(db, nome, unidade):
    from app.domain.texto import normalizar_busca

    ids = list(
        db.scalars(
            select(IdentidadeDocente.identificador)
            .join(Professor, Professor.id == IdentidadeDocente.professor_id)
            .where(
                Professor.nome_normalizado == normalizar_busca(nome),
                Professor.departamento == unidade,
            )
        )
    )
    return ids


def perfil_conhecido(db, nome, unidade):
    ids = perfis_conhecidos(db, nome, unidade)
    return ids[0] if len(ids) == 1 else None


def candidatos_locais_revisados(db, nome, unidade, candidatos):
    """Reutiliza o conjunto explicitamente revisado; perfil novo exige nova análise."""
    from app.domain.texto import normalizar_busca

    ids = {c.get("identificador") for c in candidatos}
    if len(ids) < 2 or any(
        not str(c.get("identificador", "")).isdigit()
        or normalizar_busca(c.get("nome", "")) != normalizar_busca(nome)
        for c in candidatos
    ):
        return False
    for item in db.scalars(
        select(PendenciaIdentidade).where(
            PendenciaIdentidade.unidade == unidade,
            PendenciaIdentidade.estado == "APLICADA",
            PendenciaIdentidade.motivo == "ASSOCIACAO_LOCAL_REVISADA",
        )
    ):
        if normalizar_busca(item.nome) == normalizar_busca(nome) and ids == {
            c.get("identificador") for c in item.candidatos
        }:
            return True
    return False


def pendencias_reavaliaveis(db, motivos, incluir_locais=False):
    from sqlalchemy import and_, or_

    return list(
        db.scalars(
            select(PendenciaIdentidade)
            .where(
                PendenciaIdentidade.humana.is_(False),
                or_(
                    and_(
                        PendenciaIdentidade.estado == "PENDENTE",
                        PendenciaIdentidade.motivo.in_(motivos),
                    ),
                    and_(
                        PendenciaIdentidade.estado == "APLICADA",
                        PendenciaIdentidade.motivo == "ASSOCIACAO_LOCAL",
                    )
                    if incluir_locais
                    else False,
                ),
            )
            .order_by(PendenciaIdentidade.nome, PendenciaIdentidade.id)
        )
    )


def ofertas_da_pendencia(db, item, professor_id):
    from app.models import Disciplina, Turma, Unidade
    from app.models.turma import turmas_professores

    return db.execute(
        select(Turma, Disciplina, Unidade)
        .join(Disciplina, Disciplina.id == Turma.disciplina_id)
        .join(Unidade, Unidade.id == Turma.unidade_id)
        .join(turmas_professores, turmas_professores.c.turma_id == Turma.id)
        .where(
            Unidade.fonte == "SIGAA",
            Unidade.codigo == item.unidade,
            Turma.fonte == "SIGAA",
            Turma.semestre == item.periodo,
            Turma.codigo == item.turma,
            Disciplina.codigo == item.disciplina,
            turmas_professores.c.professor_id == professor_id,
        )
    ).all()


def componente_disciplina(db, codigo):
    from app.models import Disciplina

    return db.scalar(select(Disciplina.identificador_externo).where(Disciplina.codigo == codigo))
