import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-identidades")

import unittest
from dataclasses import replace
from unittest.mock import Mock, patch
from sqlalchemy import select, func
from app.models import Professor, PendenciaIdentidade, IdentidadeDocente, Usuario
from app.schemas.identidade_docente import DecidirRequest
from app.services import identidade_docente_service as service
from app.repositories import identidade_docente_repository as repo
from app.services.sigaa_import_service import salvar_oferta
from app.scrapers.docentes import ConsultaDocentes, Disciplinas
from tests import test_reconciliacao_professores as reconciliacao_tests


CANDIDATO = {
    "identificador": "1234",
    "nome": "DOCENTE TESTE",
    "perfil_url": "https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=1234",
    "compativel": True,
}


class IdentidadeTest(unittest.TestCase):
    setUp = reconciliacao_tests.ReconciliacaoTest.setUp
    tearDown = reconciliacao_tests.ReconciliacaoTest.tearDown
    avaliar = reconciliacao_tests.ReconciliacaoTest.avaliar

    def salvar(self, turma="04", periodo="2026.2", motivo="COMPATIVEL"):
        consulta = Mock()
        consulta.consultar.return_value = (
            motivo,
            [CANDIDATO] if motivo != "CONSULTA_INCONCLUSIVA" else [],
        )
        t = salvar_oferta(
            self.db,
            replace(self.oferta, turma_codigo=turma, periodo=periodo),
            "673",
            consulta_docentes=consulta,
        )
        self.db.flush()
        return t, consulta

    def revisor(self):
        usuario = Usuario(
            nome="Revisor",
            email="identidade@aluno.unb.br",
            password_hash="x",
            email_confirmado=True,
            reconciliador=True,
        )
        self.db.add(usuario)
        self.db.flush()
        return usuario

    def item(self, turma="04"):
        return self.db.scalar(select(PendenciaIdentidade).where(PendenciaIdentidade.turma == turma))

    def test_mesmo_docente_em_turmas_semestres_e_unidades(self):
        a, _ = self.salvar()
        b, _ = self.salvar("05", "2027.1")
        c = salvar_oferta(
            self.db,
            replace(self.oferta, turma_codigo="07", unidade_id="524"),
            "524",
            consulta_docentes=Mock(consultar=Mock(return_value=("COMPATIVEL", [CANDIDATO]))),
        )
        self.assertEqual(a.professores[0].id, b.professores[0].id)
        self.assertEqual(a.professores[0].id, c.professores[0].id)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(IdentidadeDocente)), 1)
        self.assertEqual(self.item().estado, "APLICADA")

    def test_reimportacao_reutiliza_sem_consultar_fonte(self):
        a, _ = self.salvar()
        b, consulta = self.salvar()
        self.assertEqual(a.professores[0].id, b.professores[0].id)
        consulta.consultar.assert_not_called()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(PendenciaIdentidade)), 1)

    def test_homonimos_e_falhas_nao_associam(self):
        for turma, motivo in [("04", "HOMONIMOS"), ("05", "CONSULTA_INCONCLUSIVA")]:
            self.salvar(turma, motivo=motivo)
            self.assertEqual(self.item(turma).estado, "PENDENTE")
        self.assertEqual(self.db.scalar(select(func.count()).select_from(IdentidadeDocente)), 0)

    def test_moderador_de_comentario_nao_ganha_papel(self):
        u = self.revisor()
        u.reconciliador = False
        u.moderador = True
        with self.assertRaises(service.IdentidadeError) as ctx:
            service.autorizar(u)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_decisao_separar_preservada_em_reimportacao(self):
        self.salvar(motivo="HOMONIMOS")
        i = self.item()
        service.decidir(
            self.db,
            self.revisor(),
            i.id,
            DecidirRequest(acao="SEPARAR", versao=i.versao, justificativa="Pessoas diferentes"),
        )
        self.salvar()
        self.assertEqual(i.estado, "SEPARADA")
        self.assertEqual(len(repo.decisoes(self.db, i.id)), 1)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(IdentidadeDocente)), 0)

    def test_confirmacao_agenda_e_aplicacao_reutiliza_destino(self):
        self.salvar(motivo="HOMONIMOS")
        i = self.item()
        service.decidir(
            self.db,
            self.revisor(),
            i.id,
            DecidirRequest(
                acao="CONFIRMAR",
                versao=i.versao,
                identificador="1234",
                justificativa="Perfil conferido",
            ),
        )
        self.assertEqual(i.estado, "CONFIRMADA")
        self.assertIsNone(repo.identidade(self.db, "1234"))
        service.aplicar_confirmadas(self.db)
        self.assertEqual(i.estado, "APLICADA")
        novo, _ = self.salvar("05", "2027.1")
        self.assertEqual(novo.professores[0].id, i.professor_id)
        self.assertEqual(repo.decisoes(self.db, i.id)[0].identificador, "1234")

    def test_versao_obsoleta_e_perfil_fora_da_lista_recusados(self):
        self.salvar(motivo="HOMONIMOS")
        i = self.item()
        u = self.revisor()
        self.db.commit()
        for versao, identificador, status in [(99, "1234", 409), (1, "999", 422)]:
            with self.assertRaises(service.IdentidadeError) as ctx:
                service.decidir(
                    self.db,
                    u,
                    i.id,
                    DecidirRequest(
                        acao="CONFIRMAR",
                        versao=versao,
                        identificador=identificador,
                        justificativa="Teste",
                    ),
                )
            self.assertEqual(ctx.exception.status_code, status)
        self.assertEqual(repo.decisoes(self.db, i.id), [])

    def test_dados_existentes_agendam_uniao_sem_mover_avaliacao(self):
        self.avaliar(self.origem)
        self.avaliar(self.destino)
        self.salvar("02")
        self.salvar("03")
        self.assertEqual(self.item("03").estado, "CONFIRMADA")
        self.assertEqual(self.db.get(Professor, self.destino.id).id, self.destino.id)
        resultados = service.aplicar_confirmadas(self.db)
        self.assertEqual(resultados[0]["estado"], "APLICADA")
        from app.repositories.reconciliacao_professor_repository import resolver_id

        self.assertEqual(resolver_id(self.db, self.destino.id), self.origem.id)

    def test_colisao_preserva_grupo_e_avaliacoes(self):
        u = self.revisor()
        self.avaliar(self.origem, u)
        self.avaliar(self.destino, u)
        self.salvar("02")
        self.salvar("03")
        self.db.commit()
        r = service.aplicar_confirmadas(self.db)
        self.assertEqual(r[0]["estado"], "BLOQUEADA")
        self.assertEqual(self.item("03").estado, "CONFIRMADA")
        self.assertEqual(self.item("03").motivo, "APLICACAO_BLOQUEADA")
        self.assertEqual(self.origem.avaliacoes[0].professor_id, self.origem.id)
        self.assertEqual(self.destino.avaliacoes[0].professor_id, self.destino.id)

    def test_reimportacao_aplica_confirmacao_sem_uniao(self):
        self.salvar(motivo="HOMONIMOS")
        item = self.item()
        service.decidir(
            self.db,
            self.revisor(),
            item.id,
            DecidirRequest(
                acao="CONFIRMAR",
                versao=item.versao,
                identificador="1234",
                justificativa="Perfil conferido",
            ),
        )
        turma, consulta = self.salvar()
        consulta.consultar.assert_not_called()
        self.assertEqual(item.estado, "APLICADA")
        self.assertEqual(repo.identidade(self.db, "1234").professor_id, turma.professores[0].id)

    def test_nao_remapeia_professor_institucional(self):
        a, _ = self.salvar()
        with self.assertRaises(ValueError):
            repo.vincular(self.db, "9999", a.professores[0])
        self.assertIsNone(repo.identidade(self.db, "9999"))

    def test_reimportacao_nao_confirma_troca_para_outro_destino_existente(self):
        self.salvar("02", motivo="HOMONIMOS")
        repo.vincular(self.db, "9999", self.origem)
        destino, _ = self.salvar("04")
        self.salvar("02")
        item = self.item("02")
        self.assertEqual(item.estado, "PENDENTE")
        self.assertEqual(item.motivo, "CONFLITO_INSTITUCIONAL")
        self.assertIsNone(item.identificador_destino)
        self.assertEqual(self.t1.professores[0].id, self.origem.id)
        self.assertEqual(repo.identidade(self.db, "9999").professor_id, self.origem.id)
        self.assertEqual(repo.identidade(self.db, "1234").professor_id, destino.professores[0].id)

    def test_lote_revalida_identidade_de_todas_as_origens(self):
        self.salvar("04", motivo="HOMONIMOS")
        self.salvar("05", motivo="HOMONIMOS")
        a, b = self.item("04"), self.item("05")
        origem_b = repo.professor(self.db, b.professor_id)
        avaliacao = self.avaliar(origem_b)
        usuario = self.revisor()
        for item in (a, b):
            service.decidir(
                self.db,
                usuario,
                item.id,
                DecidirRequest(
                    acao="CONFIRMAR",
                    versao=item.versao,
                    identificador="1234",
                    justificativa="Perfil conferido",
                ),
            )
        # Outra ocorrência definiu uma identidade após a prévia/decisão.
        repo.vincular(self.db, "9999", origem_b)
        self.db.commit()
        resultado = service.aplicar_confirmadas(self.db)
        self.assertEqual(resultado[0]["estado"], "BLOQUEADA")
        self.assertEqual(a.estado, "CONFIRMADA")
        self.assertEqual(b.estado, "CONFIRMADA")
        self.assertIsNone(repo.identidade(self.db, "1234"))
        self.assertEqual(repo.identidade(self.db, "9999").professor_id, origem_b.id)
        self.assertEqual(reconciliacao_tests.resolver_id(self.db, origem_b.id), origem_b.id)
        self.db.refresh(avaliacao)
        self.assertEqual(avaliacao.professor_id, origem_b.id)

    def test_postgres_decisao_nao_espera_lock_da_importacao_indefinidamente(self):
        if not self.postgres:
            self.skipTest("Exige PostgreSQL descartável para verificar contenção real.")
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
        from sqlalchemy.orm import Session

        self.salvar(motivo="HOMONIMOS")
        item = self.item()
        usuario = self.revisor()
        self.db.commit()
        id_item, id_usuario, versao = item.id, usuario.id, item.versao

        def decidir_em_outra_conexao():
            with Session(self.engine) as concorrente:
                try:
                    service.decidir(
                        concorrente,
                        concorrente.get(Usuario, id_usuario),
                        id_item,
                        DecidirRequest(
                            acao="SEPARAR", versao=versao, justificativa="Pessoas distintas"
                        ),
                    )
                except service.IdentidadeError as erro:
                    return erro.status_code
                return 200

        with Session(self.engine) as importacao:
            repo.bloquear(importacao)
            with ThreadPoolExecutor(max_workers=1) as executor:
                futuro = executor.submit(decidir_em_outra_conexao)
                try:
                    status = futuro.result(timeout=8)
                except FutureTimeout:
                    importacao.rollback()
                    futuro.result(timeout=5)
                    self.fail("A decisão ficou aguardando indefinidamente o lock da importação.")
                finally:
                    importacao.rollback()
        self.assertEqual(status, 409)
        self.db.refresh(item)
        self.assertEqual(item.estado, "PENDENTE")
        self.assertEqual(repo.decisoes(self.db, id_item), [])
        service.decidir(
            self.db,
            usuario,
            id_item,
            DecidirRequest(acao="SEPARAR", versao=versao, justificativa="Pessoas distintas"),
        )
        self.assertEqual(item.estado, "SEPARADA")
        self.assertEqual(len(repo.decisoes(self.db, id_item)), 1)


class FonteTest(unittest.TestCase):
    @patch("app.scrapers.docentes.time.sleep")
    @patch("app.scrapers.docentes.ler")
    def test_busca_sem_docente_e_ausencia_nao_indisponibilidade(self, ler, sleep):
        from app.scrapers.sigaa_poc import Oferta

        ler.side_effect = [
            "<html>Portal</html>",
            '<input type="hidden" name="javax.faces.ViewState" value="estado">'
            '<select name="form:departamento"><option value="0">Todos</option></select>',
            "Nenhum docente foi encontrado de acordo com os critérios de busca informados",
        ]
        motivo, candidatos = ConsultaDocentes().consultar(
            "TESTE", Oferta("IFD0173", "Física", "01", "2026.2", ("TESTE",), "1")
        )
        self.assertEqual(motivo, "PERFIL_AUSENTE")
        self.assertEqual(candidatos, [])

    @patch("app.scrapers.docentes.time.sleep")
    @patch("app.scrapers.docentes.coletar_perfil")
    @patch("app.scrapers.docentes.buscar")
    def test_verao_preserva_perfil_e_exige_periodo_exato(self, buscar, perfil, sleep):
        from app.scrapers.sigaa_poc import Oferta

        parser = Disciplinas()
        parser.feed(
            '<div id="turmas-graduacao">'
            '<tr><td class="anoPeriodo">2026.2</td></tr>'
            '<tr><td class="codigo">IFD0173</td>'
            '<td><a href="/visualizarComponente/1">Física</a></td></tr>'
            '<tr><td class="anoPeriodo">2025.4</td></tr>'
            '<tr><td class="codigo">IFD0173</td>'
            '<td><a href="/visualizarComponente/1">Física</a></td></tr></div>'
        )
        self.assertEqual([r["periodo"] for r in parser.rows], ["2026.2", "2025.4"])
        docente = {
            "nome": "TESTE",
            "identificador_url": "1234",
            "perfil_url": "https://sigaa.unb.br",
        }
        buscar.return_value = ([], {"docentes": [docente]})
        perfil.return_value = docente | {"disciplinas": parser.rows}
        consulta = ConsultaDocentes()
        for periodo, esperado in [
            ("2026.2", "COMPATIVEL"),
            ("2025.4", "COMPATIVEL"),
            ("2025.1", "DISCIPLINA_NAO_CONFIRMADA"),
            ("2025.2", "DISCIPLINA_NAO_CONFIRMADA"),
        ]:
            with self.subTest(periodo=periodo):
                motivo, _ = consulta.consultar(
                    "TESTE", Oferta("IFD0173", "Física", "01", periodo, ("TESTE",), "1")
                )
                self.assertEqual(motivo, esperado)

    def test_ano_isolado_nao_vira_semestre(self):
        p = Disciplinas()
        p.feed(
            '<div id="turmas-graduacao"><tr><td class="anoPeriodo">2019</td></tr><tr><td class="codigo">MAT0001</td><td><a href="/visualizarComponente/1">Nome</a></td></tr></div>'
        )
        self.assertEqual(p.rows[0]["periodo"], "2019")

    @patch("app.scrapers.docentes.time.sleep")
    @patch("app.scrapers.docentes.coletar_perfil")
    @patch("app.scrapers.docentes.buscar")
    def test_nao_escolhe_homonimo_por_disciplina(self, buscar, perfil, sleep):
        from app.scrapers.sigaa_poc import Oferta

        buscar.return_value = (
            [],
            {"docentes": [{"nome": "TESTE", "identificador_url": str(i)} for i in (1, 2)]},
        )
        perfil.side_effect = lambda d: (
            d
            | {
                "perfil_url": "https://sigaa.unb.br",
                "disciplinas": [{"periodo": "2027.1", "codigo": "MAT0001", "componente_id": "1"}],
            }
        )
        motivo, candidatos = ConsultaDocentes().consultar(
            "TESTE", Oferta("MAT0001", "Nome", "01", "2027.1", ("TESTE",), "1")
        )
        self.assertEqual(motivo, "HOMONIMOS")
        self.assertEqual(len(candidatos), 2)

    def test_nome_no_corpo_nao_substitui_identidade_do_cabecalho(self):
        from app.scrapers.docentes import NomePerfil

        p = NomePerfil()
        p.feed('<h3>Nome procurado</h3><div id="id-docente"><h3>Outro Nome</h3></div>')
        self.assertEqual("".join(p.nome), "Outro Nome")


class IdentidadeHttpTest(unittest.TestCase):
    from tests import test_comentario as fixture

    setUp = fixture.ComentarioHttpIntegrationTest.setUp
    tearDown = fixture.ComentarioHttpIntegrationTest.tearDown
    _request = staticmethod(fixture.ComentarioHttpIntegrationTest._request)

    def criar_item(self):
        item = PendenciaIdentidade(
            chave="HTTP:TESTE",
            professor_id=self.professor.id,
            nome=self.professor.nome,
            unidade="CIC",
            periodo="2027.1",
            disciplina="CIC0098",
            turma="01",
            motivo="HOMONIMOS",
            candidatos=[CANDIDATO],
            estado="PENDENTE",
        )
        self.db.add(item)
        self.db.commit()
        return item

    def test_fila_privada_permissao_separada_e_decisao_auditada(self):
        import asyncio

        item = self.criar_item()
        path = "/api/moderacao/identidades"
        status, _ = asyncio.run(self._request("GET", path))
        self.assertEqual(status, 401)
        self.usuario.moderador = True
        self.db.commit()
        status, _ = asyncio.run(self._request("GET", path, token=self.token))
        self.assertEqual(status, 403)
        self.usuario.reconciliador = True
        self.db.commit()
        status, lista = asyncio.run(self._request("GET", path, token=self.token))
        self.assertEqual(status, 200)
        self.assertEqual(lista[0]["id"], str(item.id))
        status, resultado = asyncio.run(
            self._request(
                "POST",
                f"{path}/{item.id}/decisoes",
                {
                    "acao": "CONFIRMAR",
                    "versao": 1,
                    "identificador": "1234",
                    "justificativa": "Verificado no perfil",
                },
                self.token,
            )
        )
        self.assertEqual(status, 200, resultado)
        self.assertEqual(resultado["estado"], "CONFIRMADA")
        status, decisoes = asyncio.run(
            self._request("GET", f"{path}/{item.id}/decisoes", token=self.token)
        )
        self.assertEqual(status, 200)
        self.assertEqual(decisoes[0]["usuario_id"], str(self.usuario.id))
        status, _ = asyncio.run(
            self._request(
                "POST",
                f"{path}/{item.id}/decisoes",
                {"acao": "SEPARAR", "versao": 1, "justificativa": "Outra aba antiga"},
                self.token,
            )
        )
        self.assertEqual(status, 409)
