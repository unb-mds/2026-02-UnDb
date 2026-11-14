"""Contrato híbrido autorizado pelo PO; fixtures locais, sem consulta ao SIGAA."""

import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-hibrido")
from dataclasses import replace
from unittest.mock import Mock
from sqlalchemy import select, func, event
from app.models import PendenciaIdentidade, IdentidadeLocal
from app.models.professor_correspondencia import ProfessorCorrespondencia
from app.repositories import identidade_docente_repository as repo
from app.repositories import reconciliacao_professor_repository as reconciliacao
from app.services import identidade_docente_service as service
from app.services.sigaa_import_service import salvar_oferta
from tests import test_identidade_docente as fixture


class HibridoTest(unittest.TestCase):
    setUp = fixture.IdentidadeTest.setUp
    tearDown = fixture.IdentidadeTest.tearDown
    avaliar = fixture.IdentidadeTest.avaliar
    salvar = fixture.IdentidadeTest.salvar
    item = fixture.IdentidadeTest.item
    revisor = fixture.IdentidadeTest.revisor

    def oferta_local(self, turma, periodo="2026.2", unidade="673", motivo="PERFIL_AUSENTE"):
        return salvar_oferta(
            self.db,
            replace(self.oferta, turma_codigo=turma, periodo=periodo, unidade_id=unidade),
            unidade,
            consulta_docentes=Mock(consultar=Mock(return_value=(motivo, []))),
        )

    def test_reutiliza_nome_unidade_em_turmas_e_semestres(self):
        a = self.oferta_local("04")
        b = self.oferta_local("05", "2027.1")
        c = self.oferta_local("04")
        self.assertEqual(
            {a.professores[0].id, b.professores[0].id, c.professores[0].id}, {a.professores[0].id}
        )
        self.assertEqual(self.db.scalar(select(func.count()).select_from(IdentidadeLocal)), 1)
        self.assertEqual(self.item("04").motivo, "ASSOCIACAO_LOCAL")
        self.assertIsNone(repo.identidade_do_professor(self.db, a.professores[0].id))

    def test_nao_agrupa_entre_unidades(self):
        a = self.oferta_local("04")
        b = self.oferta_local("04", unidade="524")
        self.assertNotEqual(a.professores[0].id, b.professores[0].id)

    def test_promocao_preserva_uuid_e_avaliacao(self):
        a = self.oferta_local("04")
        id = a.professores[0].id
        avaliacao = self.avaliar(a.professores[0])
        antes = avaliacao.id
        self.salvar("04")
        self.assertEqual(repo.identidade(self.db, "1234").professor_id, id)
        self.assertEqual(avaliacao.id, antes)
        self.assertEqual(self.item("04").professor_id, id)
        b, _ = self.salvar("05", "2027.1")
        self.assertEqual(b.professores[0].id, id)

    def test_perfil_aparece_em_nova_turma_promove_local(self):
        a = self.oferta_local("04")
        b, _ = self.salvar("05", "2027.1")
        self.assertEqual(a.professores[0].id, b.professores[0].id)

    def test_falha_ou_ambiguidade_nao_acionam_fallback(self):
        for i, motivo in enumerate(["CONSULTA_INCONCLUSIVA", "HOMONIMOS"]):
            self.oferta_local(str(10 + i), motivo=motivo)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(IdentidadeLocal)), 0)

    def test_historico_incompleto_reutiliza_identidade_no_semestre_seguinte(self):
        a = self.oferta_local("04", motivo="DISCIPLINA_NAO_CONFIRMADA")
        b = self.oferta_local("05", "2027.1", motivo="DISCIPLINA_NAO_CONFIRMADA")
        self.assertEqual(a.professores[0].id, b.professores[0].id)
        self.assertIsNone(repo.identidade_do_professor(self.db, a.professores[0].id))

    def test_historico_incompleto_reutiliza_canonico_institucional_existente(self):
        repo.vincular(self.db, "1234", self.destino)
        a = self.oferta_local("04", motivo="DISCIPLINA_NAO_CONFIRMADA")
        self.assertEqual(a.professores[0].id, self.destino.id)
        self.assertEqual(self.item("04").estado, "APLICADA")

    def oferta_multiplos(self, turma, periodo="2026.2", segundo="5678", unidade="673"):
        candidatos = [fixture.CANDIDATO, dict(fixture.CANDIDATO, identificador=segundo)]
        return salvar_oferta(
            self.db,
            replace(self.oferta, turma_codigo=turma, periodo=periodo, unidade_id=unidade),
            unidade,
            consulta_docentes=Mock(consultar=Mock(return_value=("HOMONIMOS", candidatos))),
        )

    def test_multiplos_revisados_reutilizados_sem_aceitar_perfil_novo(self):
        a = self.oferta_multiplos("04")
        b = self.oferta_multiplos("05")
        avaliacao = self.avaliar(a.professores[0])
        avaliacao_id = avaliacao.id
        self.db.commit()
        self.assertEqual(service.consolidar_locais(self.db), [])
        previa = service.consolidar_locais(self.db, incluir_revisadas=True)
        self.assertEqual(previa[0]["registros_a_unir"], 1)
        self.assertIsNone(repo.local(self.db, "DOCENTE TESTE", "673"))
        resultado = service.consolidar_locais(self.db, True, incluir_revisadas=True)
        self.assertEqual(resultado[0]["estado"], "APLICADA")
        destino = repo.local(self.db, "DOCENTE TESTE", "673").professor_id
        self.db.expire_all()
        self.assertEqual(a.professores[0].id, destino)
        self.assertEqual(b.professores[0].id, destino)
        self.assertEqual(avaliacao.id, avaliacao_id)
        self.assertEqual(avaliacao.professor_id, destino)
        futuro = self.oferta_multiplos("06", "2027.1")
        self.assertEqual(futuro.professores[0].id, destino)
        self.assertEqual(self.item("06").estado, "APLICADA")
        novo = self.oferta_multiplos("07", "2027.1", segundo="9999")
        self.assertNotEqual(novo.professores[0].id, destino)
        self.assertEqual(self.item("07").estado, "PENDENTE")
        outra = self.oferta_multiplos("08", "2027.1", unidade="524")
        self.assertNotEqual(outra.professores[0].id, destino)
        self.assertEqual(self.item("08").estado, "PENDENTE")
        self.oferta_local("04", motivo="CONSULTA_INCONCLUSIVA")
        self.assertTrue(
            repo.candidatos_locais_revisados(
                self.db,
                "DOCENTE TESTE",
                "673",
                [fixture.CANDIDATO, dict(fixture.CANDIDATO, identificador="5678")],
            )
        )

    def test_indisponibilidade_reutiliza_local_apos_revisao_explicita(self):
        self.oferta_local("04", motivo="CONSULTA_INCONCLUSIVA")
        self.db.commit()
        self.assertEqual(service.consolidar_locais(self.db), [])
        self.assertEqual(
            service.consolidar_locais(self.db, True, incluir_revisadas=True)[0]["estado"],
            "APLICADA",
        )
        destino = repo.local(self.db, "DOCENTE TESTE", "673").professor_id
        futuro = self.oferta_local("05", "2027.1", motivo="CONSULTA_INCONCLUSIVA")
        self.assertEqual(futuro.professores[0].id, destino)

    def test_revisao_explicita_nao_descarta_avaliacoes_em_colisao(self):
        a = self.oferta_multiplos("04")
        b = self.oferta_multiplos("05")
        avaliacao = self.avaliar(a.professores[0])
        self.avaliar(b.professores[0], avaliacao.usuario)
        self.db.commit()
        resultado = service.consolidar_locais(self.db, True, incluir_revisadas=True)
        self.assertEqual(resultado[0]["estado"], "BLOQUEADA")
        self.assertIn("Colisão", resultado[0]["erro"])
        self.assertIsNone(repo.local(self.db, "DOCENTE TESTE", "673"))
        self.assertEqual(self.item("04").estado, "PENDENTE")
        self.assertEqual(self.item("05").estado, "PENDENTE")

    def test_multiplos_sem_evidencia_valida_bloqueiam_revisao(self):
        self.salvar("04", motivo="HOMONIMOS")
        self.db.commit()
        self.assertEqual(
            service.consolidar_locais(self.db, True, incluir_revisadas=True)[0]["estado"],
            "BLOQUEADA",
        )
        self.assertIsNone(repo.local(self.db, "DOCENTE TESTE", "673"))

    def test_decisao_humana_separada_impede_fallback_em_nova_turma(self):
        self.salvar("04", motivo="HOMONIMOS")
        from app.schemas.identidade_docente import DecidirRequest

        item = self.item("04")
        service.decidir(
            self.db,
            self.revisor(),
            item.id,
            DecidirRequest(acao="SEPARAR", versao=item.versao, justificativa="Pessoas distintas"),
        )
        self.oferta_local("05")
        self.assertEqual(self.item("05").estado, "PENDENTE")
        self.assertEqual(self.db.scalar(select(func.count()).select_from(IdentidadeLocal)), 0)

    def test_consolidacao_local_previa_aplicacao_e_repeticao(self):
        # Reproduzir os dois registros legados da fixture.
        for t in (self.t1, self.t2):
            self.db.add(
                PendenciaIdentidade(
                    chave="pendente:" + str(t.id),
                    professor_id=t.professores[0].id,
                    nome="DOCENTE TESTE",
                    unidade="673",
                    periodo="2026.2",
                    disciplina=self.oferta.componente_codigo,
                    turma=t.codigo,
                    motivo="PERFIL_AUSENTE",
                    estado="PENDENTE",
                )
            )
        self.db.commit()
        a = service.consolidar_locais(self.db)
        self.assertEqual(a[0]["registros_a_unir"], 1)
        self.assertEqual(
            self.db.scalar(select(func.count()).select_from(ProfessorCorrespondencia)), 0
        )
        progresso = []
        r = service.consolidar_locais(self.db, True, lambda n, t, r: progresso.append((n, t)))
        self.assertEqual(r[0]["estado"], "APLICADA")
        self.assertEqual(progresso, [(1, 1)])
        self.assertEqual(service.consolidar_locais(self.db, True), [])
        self.db.expire_all()
        self.assertEqual(self.t1.professores[0].id, self.t2.professores[0].id)

    def test_local_antigo_agenda_manutencao_sem_confirmada_nula(self):
        self.oferta_local("04")
        self.oferta_local("02")
        self.assertEqual(self.item("02").estado, "PENDENTE")
        self.assertEqual(self.item("02").motivo, "PERFIL_AUSENTE")
        self.assertEqual(service.aplicar_confirmadas(self.db), [])
        self.assertEqual(service.consolidar_locais(self.db, True)[0]["estado"], "APLICADA")

    def test_lote_detecta_colisao_entre_origens(self):
        terceira = self.oferta_local("04").professores[0]
        a = self.avaliar(self.origem)
        self.avaliar(self.destino, a.usuario)
        with self.assertRaisesRegex(ValueError, "Colisão"):
            reconciliacao.aplicar_grupo_em_lote(
                self.db, [self.origem.id, self.destino.id], terceira.id, "Teste"
            )
        self.db.rollback()
        self.assertEqual(reconciliacao.resolver_id(self.db, self.origem.id), self.origem.id)

    def test_lote_reduz_queries_e_preserva_links_antigos(self):
        self.db.commit()
        consultas = []

        def contar(*args):
            consultas.append(args[2])

        event.listen(self.engine, "before_cursor_execute", contar)
        try:
            reconciliacao.aplicar_grupo_em_lote(self.db, [self.origem.id], self.destino.id, "Teste")
            self.db.commit()
        finally:
            event.remove(self.engine, "before_cursor_execute", contar)
        # Sem round trips individuais por turma/avaliação; total medido no dialeto.
        self.assertLess(len(consultas), 25)
        self.assertEqual(reconciliacao.resolver_id(self.db, self.origem.id), self.destino.id)
        terceira = self.oferta_local("04").professores[0]
        reconciliacao.aplicar_grupo_em_lote(self.db, [self.destino.id], terceira.id, "Promoção")
        self.db.commit()
        self.assertEqual(reconciliacao.resolver_id(self.db, self.origem.id), terceira.id)
        self.assertEqual(reconciliacao.resolver_id(self.db, self.destino.id), terceira.id)

    def test_grupo_concluido_persiste_antes_do_proximo(self):
        self.salvar("02")
        self.salvar("03")
        vistos = []

        def progresso(n, t, r):
            vistos.append(r["estado"])
            raise RuntimeError("Interrupção após commit")

        with self.assertRaises(RuntimeError):
            service.aplicar_confirmadas(self.db, progresso)
        self.db.rollback()
        self.assertEqual(vistos, ["APLICADA"])
        self.assertEqual(service.aplicar_confirmadas(self.db), [])

    def test_perfil_manual_promove_local_ja_aplicado(self):
        from app.commands.reavaliar_identidades import carregar, aplicar
        from app.scrapers.docentes import normalizar

        a = self.oferta_local("04")
        id = a.professores[0].id
        self.db.commit()
        itens, _ = carregar(self.db, ("PERFIL_AUSENTE",), {normalizar("DOCENTE TESTE")}, True)
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0].motivo, "ASSOCIACAO_LOCAL")
        consulta = Mock(consultar=Mock(return_value=("COMPATIVEL", [fixture.CANDIDATO])))
        self.assertEqual(aplicar(self.db, itens[0], consulta, ("PERFIL_AUSENTE",)), "APLICADA")
        self.assertEqual(repo.identidade(self.db, "1234").professor_id, id)

    def test_perfil_conhecido_nao_depende_da_busca_encontra_lo(self):
        from app.scrapers.docentes import ConsultaDocentes
        from unittest.mock import patch

        a, _ = self.salvar("04")
        perfil = {
            "nome": "DOCENTE TESTE",
            "identificador_url": "1234",
            "perfil_url": fixture.CANDIDATO["perfil_url"],
            "disciplinas": [
                {
                    "periodo": "2027.1",
                    "codigo": self.oferta.componente_codigo,
                    "componente_id": self.oferta.componente_id,
                }
            ],
        }
        with (
            patch("app.scrapers.docentes.buscar", return_value=([], {"docentes": []})),
            patch("app.scrapers.docentes.coletar_perfil", return_value=perfil),
            patch("app.scrapers.docentes.time.sleep"),
        ):
            b = salvar_oferta(
                self.db,
                replace(self.oferta, turma_codigo="05", periodo="2027.1"),
                "673",
                consulta_docentes=ConsultaDocentes(),
            )
        self.assertEqual(a.professores[0].id, b.professores[0].id)
        self.assertEqual(self.item("05").motivo, "COMPATIVEL")

    def test_perfil_indicado_nao_elimina_outro_candidato(self):
        from app.scrapers.docentes import ConsultaDocentes, normalizar
        from unittest.mock import patch

        consulta = ConsultaDocentes()
        p = {
            "nome": "DOCENTE TESTE",
            "identificador_url": "1234",
            "perfil_url": fixture.CANDIDATO["perfil_url"],
            "disciplinas": [],
        }
        consulta.cache[normalizar(p["nome"])] = [p]
        with patch(
            "app.scrapers.docentes.coletar_perfil", return_value=p | {"identificador_url": "5678"}
        ):
            consulta.registrar_perfil(p["nome"], "5678")
        motivo, candidatos = consulta.consultar(p["nome"], self.oferta)
        self.assertEqual(motivo, "HOMONIMOS")
        self.assertEqual(len(candidatos), 2)

    def test_migration_local_aditiva_e_preserva_associacoes(self):
        import importlib.util
        from pathlib import Path
        from alembic.migration import MigrationContext
        from alembic.operations import Operations

        path = Path(__file__).parents[1] / "alembic/versions/20261113_01_identidades_locais.py"
        spec = importlib.util.spec_from_file_location("migration_hibrido", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        self.db.rollback()
        with self.engine.begin() as connection:
            IdentidadeLocal.__table__.drop(connection)
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
                migration.downgrade()
                migration.upgrade()
        self.oferta_local("04")
        self.db.commit()
        with self.engine.begin() as connection:
            with Operations.context(MigrationContext.configure(connection)):
                with self.assertRaises(RuntimeError):
                    migration.downgrade()

    def test_falha_de_escrita_desfaz_grupo_inteiro(self):
        self.salvar("02")
        self.salvar("03")
        self.db.commit()

        def falhar(conn, cursor, statement, *args):
            if statement.startswith("UPDATE avaliacoes"):
                raise RuntimeError("Falha de escrita simulada")

        event.listen(self.engine, "before_cursor_execute", falhar)
        try:
            with self.assertRaises(RuntimeError):
                service.aplicar_confirmadas(self.db)
        finally:
            event.remove(self.engine, "before_cursor_execute", falhar)
        self.db.rollback()
        self.db.expire_all()
        self.assertEqual(self.item("03").estado, "CONFIRMADA")
        self.assertEqual(self.t1.professores[0].id, self.origem.id)
        self.assertEqual(reconciliacao.resolver_id(self.db, self.destino.id), self.destino.id)

    def test_fallback_nao_contorna_duas_identidades_conhecidas(self):
        repo.vincular(self.db, "1234", self.origem)
        repo.vincular(self.db, "5678", self.destino)
        self.oferta_local("04")
        self.assertEqual(self.item("04").estado, "PENDENTE")
        self.assertEqual(self.item("04").motivo, "CONFLITO_INSTITUCIONAL")
        self.assertEqual(self.db.scalar(select(func.count()).select_from(IdentidadeLocal)), 0)

    def test_cli_previa_nao_escreve_e_aplicacao_exige_manutencao(self):
        from app.commands import identidades
        from contextlib import redirect_stdout, redirect_stderr
        from unittest.mock import patch
        import io
        import json

        self.oferta_local("04")
        self.oferta_local("02")
        self.db.commit()
        saida = io.StringIO()
        with (
            patch("sys.argv", ["identidades", "locais"]),
            patch.object(identidades, "SessionLocal", return_value=self.db),
            redirect_stdout(saida),
            redirect_stderr(io.StringIO()),
        ):
            identidades.main()
        self.assertEqual(json.loads(saida.getvalue())[0]["estado"], "PREVIA")
        with (
            patch("sys.argv", ["identidades", "locais", "--aplicar"]),
            patch.object(identidades, "SessionLocal", return_value=self.db),
            redirect_stderr(io.StringIO()),
        ):
            with self.assertRaises(SystemExit) as erro:
                identidades.main()
        self.assertEqual(erro.exception.code, 2)
