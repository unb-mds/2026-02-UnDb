from sqlalchemy.exc import OperationalError
from app.models.identidade_docente import PendenciaIdentidade, DecisaoIdentidade
from app.repositories import identidade_docente_repository as repo, professor_repository
from app.repositories import reconciliacao_professor_repository as reconciliacao


class IdentidadeError(ValueError):
    def __init__(self, status_code, mensagem):
        self.status_code = status_code
        super().__init__(mensagem)


def autorizar(usuario):
    if not usuario.email_confirmado or not usuario.reconciliador:
        raise IdentidadeError(403, "Permissão de revisão de identidades necessária.")


def resolver(db, nome, departamento, chave, oferta, consulta):
    repo.bloquear(db)
    anterior = repo.obter(db, chave)
    if (
        anterior
        and anterior.estado in ("APLICADA", "SEPARADA", "CONFIRMADA")
        and anterior.motivo != "ASSOCIACAO_LOCAL"
    ):
        origem = repo.professor(db, anterior.professor_id)
        if anterior.estado == "CONFIRMADA":
            institucional = repo.identidade(db, anterior.identificador_destino)
            # Registrar identidade sem mover dependentes é seguro no importador.
            # A união de UUIDs distintos permanece na janela administrativa.
            if (
                institucional is None
                or repo.professor(db, institucional.professor_id).id == origem.id
            ):
                try:
                    repo.vincular(db, anterior.identificador_destino, origem)
                    anterior.estado = "APLICADA"
                    anterior.versao += 1
                    db.flush()
                except ValueError:
                    anterior.motivo = "APLICACAO_BLOQUEADA"
        return origem
    # Correspondências explícitas da #223 têm precedência sobre inferências novas.
    origem = (
        repo.professor(db, anterior.professor_id)
        if anterior
        else professor_repository.get_by_identidade_origem(db, chave)
    )
    if (
        origem
        and reconciliacao.resolver_id(db, origem.id) != origem.id
        and not (anterior and anterior.motivo == "ASSOCIACAO_LOCAL")
    ):
        return repo.professor(db, origem.id)
    motivo, candidatos = consulta.consultar(nome, oferta)
    from app.scrapers.docentes import ConsultaDocentes

    if motivo == "PERFIL_AUSENTE" and isinstance(consulta, ConsultaDocentes):
        conhecido = repo.perfil_conhecido(db, nome, departamento)
        if conhecido:
            try:
                consulta.registrar_perfil(nome, conhecido)
                motivo, candidatos = consulta.consultar(nome, oferta)
            except Exception:
                motivo, candidatos = "CONSULTA_INCONCLUSIVA", []
    destino = None
    identificador = None
    if motivo == "COMPATIVEL" and len(candidatos) == 1:
        identificador = candidatos[0]["identificador"]
        institucional = repo.identidade(db, identificador)
        if institucional:
            destino = repo.professor(db, institucional.professor_id)
    # Um cadastro local pode receber perfil posteriormente sem trocar seu UUID.
    associacao_local = repo.local(db, nome, departamento)
    if origem is None and associacao_local and motivo == "COMPATIVEL":
        origem = repo.professor(db, associacao_local.professor_id)
    if motivo == "PERFIL_AUSENTE" and len(repo.perfis_conhecidos(db, nome, departamento)) > 1:
        motivo = "CONFLITO_INSTITUCIONAL"
    if motivo == "PERFIL_AUSENTE" and not repo.separacao_humana(db, nome, departamento):
        if associacao_local:
            destino = repo.professor(db, associacao_local.professor_id)
        else:
            origem = origem or professor_repository.get_or_create_provisorio(
                db, nome, departamento, chave
            )
            destino = repo.vincular_local(db, nome, departamento, origem)
        motivo = "ASSOCIACAO_LOCAL"
    if origem is None:
        origem = destino or professor_repository.get_or_create_provisorio(
            db, nome, departamento, chave
        )
    if identificador:
        try:
            destino = repo.vincular(db, identificador, origem)
        except ValueError:
            motivo = "CONFLITO_INSTITUCIONAL"
            identificador = None
            destino = None
    # UUIDs antigos distintos exigem manutenção; nunca agendar perfil NULL como SIAPE.
    if motivo == "ASSOCIACAO_LOCAL" and destino and destino.id != origem.id:
        motivo = "PERFIL_AUSENTE"
        destino = None
    estado = (
        "APLICADA"
        if destino and destino.id == origem.id
        else "CONFIRMADA"
        if destino
        else "PENDENTE"
    )
    if anterior is None:
        anterior = PendenciaIdentidade(
            chave=chave,
            professor_id=origem.id,
            nome=nome,
            unidade=departamento,
            periodo=oferta.periodo,
            disciplina=oferta.componente_codigo,
            turma=oferta.turma_codigo,
        )
        db.add(anterior)
    else:
        anterior.versao += 1
    anterior.motivo = motivo
    anterior.candidatos = candidatos
    anterior.estado = estado
    anterior.identificador_destino = identificador
    db.flush()
    return origem


def decidir(db, usuario, id, dados):
    autorizar(usuario)
    try:
        repo.bloquear(db)
        item = repo.por_id(db, id)
        if item is None:
            raise IdentidadeError(404, "Pendência não encontrada.")
        if item.versao != dados.versao or item.estado != "PENDENTE":
            raise IdentidadeError(409, "Pendência alterada. Atualize a fila antes de decidir.")
        identificador = dados.identificador
        if dados.acao == "CONFIRMAR":
            if identificador not in {c["identificador"] for c in item.candidatos}:
                raise IdentidadeError(422, "Escolha um dos perfis institucionais apresentados.")
            if previa(db, item, identificador)["bloqueada"]:
                raise IdentidadeError(409, "Colisão de avaliações: associação bloqueada.")
            item.estado = "CONFIRMADA"
            item.identificador_destino = identificador
        else:
            if identificador is not None:
                raise IdentidadeError(422, "Manter separados não aceita perfil de destino.")
            item.estado = "SEPARADA"
        db.add(
            DecisaoIdentidade(
                pendencia_id=item.id,
                usuario_id=usuario.id,
                acao=dados.acao,
                justificativa=dados.justificativa,
                identificador=identificador,
                versao=item.versao,
            )
        )
        item.humana = True
        item.versao += 1
        db.commit()
        return item
    except OperationalError as erro:
        db.rollback()
        if getattr(erro.orig, "pgcode", None) == "55P03":
            raise IdentidadeError(
                409, "Fila em atualização. Aguarde e atualize a fila antes de decidir."
            ) from erro
        raise
    except Exception:
        db.rollback()
        raise


def aplicar_confirmadas(db, progresso=None):
    """Commit por grupo: progresso durável e retomada sem repetir grupos concluídos."""
    grupos = repo.grupos_confirmados(db)
    db.commit()
    resultados = []
    for numero, (identificador, ids) in enumerate(grupos.items(), 1):
        itens = []
        try:
            repo.bloquear(db)
            reconciliacao._bloquear_escritas(db)
            itens = [
                i
                for i in repo.itens_por_ids(db, ids)
                if i.estado == "CONFIRMADA" and i.identificador_destino == identificador
            ]
            if not itens:
                db.rollback()
                continue
            with db.begin_nested():
                destino, origens = repo.vincular_grupo(
                    db, identificador, [i.professor_id for i in itens]
                )
                if origens:
                    reconciliacao.aplicar_grupo_em_lote(
                        db,
                        origens,
                        destino.id,
                        "Associação institucional #207; fila e decisões auditadas.",
                    )
                for item in itens:
                    item.estado = "APLICADA"
                    item.professor_id = destino.id
                    item.versao += 1
                db.flush()
            resultado = {
                "identificador": identificador,
                "estado": "APLICADA",
                "ocorrencias": len(itens),
            }
        except ValueError as erro:
            for item in itens:
                item.motivo = "APLICACAO_BLOQUEADA"
                item.versao += 1
            resultado = {"identificador": identificador, "estado": "BLOQUEADA", "erro": str(erro)}
        except BaseException:
            db.rollback()
            raise
        db.commit()
        resultados.append(resultado)
        if progresso:
            progresso(numero, len(grupos), resultado)
    return resultados


def previa(db, item, identificador):
    if identificador not in {c["identificador"] for c in item.candidatos}:
        raise IdentidadeError(422, "Perfil não apresentado nesta pendência.")
    identidade = repo.identidade(db, identificador)
    origem = repo.professor(db, item.professor_id)
    destino = repo.professor(db, identidade.professor_id) if identidade else origem
    existente = repo.identidade_do_professor(db, origem.id)
    if (existente and existente.identificador != identificador) or (
        origem.siape and origem.siape != identificador
    ):
        raise IdentidadeError(409, "O registro já possui outra identidade institucional.")
    if destino.id == origem.id:
        return {"colisoes": 0, "uniao_necessaria": False, "bloqueada": False}
    try:
        plano = reconciliacao.planejar(db, origem.id, destino.id)
    except reconciliacao.ReconciliacaoRecusada as erro:
        raise IdentidadeError(409, str(erro)) from erro
    return {
        "colisoes": plano["colisoes"],
        "uniao_necessaria": True,
        "bloqueada": bool(plano["colisoes"]),
        "turmas": plano["turmas"],
        "avaliacoes": plano["avaliacoes"],
    }


def consolidar_locais(db, aplicar=False, progresso=None):
    """Prévia por padrão; aplicar somente na janela administrativa de manutenção."""
    grupos = repo.grupos_locais(db)
    db.commit()
    resultados = []
    for numero, ((nome, unidade), ids) in enumerate(grupos.items(), 1):
        itens = []
        try:
            if aplicar:
                repo.bloquear(db)
                reconciliacao._bloquear_escritas(db)
            itens = [
                i
                for i in repo.itens_por_ids(db, ids)
                if i.estado == "PENDENTE" and i.motivo == "PERFIL_AUSENTE" and not i.humana
            ]
            if not itens:
                db.rollback()
                continue
            destino, origens = repo.destino_local_grupo(
                db, itens[0].nome, unidade, [i.professor_id for i in itens]
            )
            resultado = {
                "nome": nome,
                "unidade": unidade,
                "ocorrencias": len(itens),
                "registros_a_unir": len(origens),
                "estado": "APLICADA" if aplicar else "PREVIA",
            }
            if origens and not aplicar:
                reconciliacao.validar_grupo_em_lote(
                    db, origens, destino.id, "Prévia do fallback nome + unidade #207."
                )
            if aplicar:
                with db.begin_nested():
                    if origens:
                        reconciliacao.aplicar_grupo_em_lote(
                            db,
                            origens,
                            destino.id,
                            "Fallback nome completo + unidade #207; risco residual aceito pelo PO.",
                        )
                    repo.vincular_local(db, itens[0].nome, unidade, destino)
                    for item in itens:
                        item.professor_id = destino.id
                        item.estado = "APLICADA"
                        item.motivo = "ASSOCIACAO_LOCAL"
                        item.identificador_destino = None
                        item.versao += 1
                    db.flush()
        except ValueError as erro:
            resultado = {"nome": nome, "unidade": unidade, "estado": "BLOQUEADA", "erro": str(erro)}
        except BaseException:
            db.rollback()
            raise
        if aplicar:
            db.commit()
        else:
            db.rollback()
        resultados.append(resultado)
        if progresso:
            progresso(numero, len(grupos), resultado)
    return resultados
