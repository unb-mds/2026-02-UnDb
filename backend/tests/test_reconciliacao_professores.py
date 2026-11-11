import os
import unittest
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from datetime import UTC, datetime, timedelta
from dataclasses import replace
from uuid import uuid4
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-reconciliacao")

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.routers.professores import consultar_avaliacoes_professor_disciplina
from app.routers.disciplinas import comparar_professores_da_disciplina
from app.models import Avaliacao, ComentarioVersao, Professor, Usuario
from app.models.enums import Dificuldade, EstadoComentario
from app.models.professor_correspondencia import ProfessorCorrespondencia
from app.models.denuncia import Denuncia
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.enums import MotivoDenuncia
from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.repositories import professor_repository as professores
from app.repositories.reconciliacao_professor_repository import (
    ReconciliacaoRecusada,
    aplicar,
    aplicar_grupo,
    planejar,
    planejar_grupo,
    resolver_id,
)
from app.scrapers.sigaa_poc import Oferta
from app.services.sigaa_import_service import salvar_oferta
from app.services import institucional_service
from app.commands import reconciliar_professores


class ReconciliacaoTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
        )
        event.listen(self.engine, "connect", lambda db, _: db.execute("PRAGMA foreign_keys=ON"))
        # SQLite legacy não inicia transação em SELECT antes de SAVEPOINT;
        # usar BEGIN explícito reproduz a semântica transacional do PostgreSQL.
        event.listen(self.engine, "connect", lambda db, _: setattr(db, "isolation_level", None))
        event.listen(self.engine, "begin", lambda connection: connection.exec_driver_sql("BEGIN"))
        postgres_url = os.environ.get("RECONCILIACAO_POSTGRES_TEST_URL")
        self.postgres = bool(postgres_url)
        if postgres_url:
            url = make_url(postgres_url)
            if url.get_backend_name() != "postgresql" or url.database != "undb_207_test":
                raise ValueError("Usar somente PostgreSQL descartável com banco undb_207_test.")
            self.engine.dispose()
            self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.oferta = Oferta(
            componente_codigo="FGA0312",
            componente_nome="MDS",
            turma_codigo="02",
            periodo="2026.2",
            docentes=("DOCENTE TESTE",),
            componente_id="315739",
            unidade_id="673",
        )
        self.t1 = salvar_oferta(self.db, self.oferta, "673")
        self.origem = self.t1.professores[0]
        self.t2 = salvar_oferta(self.db, replace(self.oferta, turma_codigo="03"), "673")
        self.destino = self.t2.professores[0]
        self.db.commit()

    def tearDown(self):
        self.db.close()
        if self.postgres:
            Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def avaliar(self, professor, usuario=None):
        if usuario is None:
            usuario = Usuario(
                nome="Teste", email=f"{uuid4()}@aluno.unb.br", password_hash="fixture"
            )
            self.db.add(usuario)
            self.db.flush()
        avaliacao = Avaliacao(
            usuario_id=usuario.id,
            professor_id=professor.id,
            disciplina_id=self.t1.disciplina_id,
            didatica=4,
            dificuldade=Dificuldade.MEDIO,
            chamada=True,
            disponibiliza_material=False,
            qualidade_material=None,
            recomenda=True,
        )
        self.db.add(avaliacao)
        self.db.commit()
        return avaliacao

    def aplicar(self):
        result = aplicar(
            self.db, self.origem.id, self.destino.id, "Confirmação humana documentada no teste"
        )
        self.db.commit()
        return result

    def test_simulacao_nao_muda_dados_e_nome_igual_nao_funde(self):
        self.assertEqual(len(professores.listar(self.db)), 2)
        self.assertEqual(planejar(self.db, self.origem.id, self.destino.id)["turmas"], 1)
        self.assertEqual(len(professores.listar(self.db)), 2)
        self.assertEqual(
            self.db.scalar(select(func.count()).select_from(ProfessorCorrespondencia)), 0
        )

    def test_preserva_origem_id_avaliacao_e_versoes(self):
        avaliacao = self.avaliar(self.origem)
        comentario = ComentarioVersao(
            avaliacao_id=avaliacao.id,
            texto="Comentário de teste",
            estado=EstadoComentario.PUBLICADO,
        )
        self.db.add(comentario)
        self.db.commit()
        agora = datetime.now(UTC)
        denuncia = Denuncia(
            comentario_versao_id=comentario.id,
            denunciante_id=avaliacao.usuario_id,
            motivo=MotivoDenuncia.SPAM,
            created_at=agora,
        )
        decisao = DecisaoModeracao(
            comentario_versao_id=comentario.id,
            moderador_id=avaliacao.usuario_id,
            acao="APROVAR",
            motivo="Fixture",
            estado_anterior="PENDENTE",
            estado_posterior="PUBLICADO",
            created_at=agora,
            descartar_em=agora + timedelta(days=7),
        )
        self.db.add_all([denuncia, decisao])
        self.db.commit()
        relacionados = (
            denuncia.id,
            denuncia.comentario_versao_id,
            decisao.id,
            decisao.comentario_versao_id,
        )
        antes = (
            avaliacao.id,
            avaliacao.created_at,
            avaliacao.updated_at,
            comentario.id,
            comentario.avaliacao_id,
        )
        self.aplicar()
        self.db.expire_all()
        self.assertEqual(avaliacao.professor_id, self.destino.id)
        self.assertEqual(
            antes,
            (
                avaliacao.id,
                avaliacao.created_at,
                avaliacao.updated_at,
                comentario.id,
                comentario.avaliacao_id,
            ),
        )
        self.assertIsNotNone(self.db.get(Professor, self.origem.id))
        self.assertEqual(
            relacionados,
            (denuncia.id, denuncia.comentario_versao_id, decisao.id, decisao.comentario_versao_id),
        )
        self.assertEqual([p.id for p in professores.listar(self.db)], [self.destino.id])
        self.assertEqual([p.id for p in self.t1.professores], [self.destino.id])

    def test_reimportacao_e_repeticao_nao_recriam_fragmentacao(self):
        self.aplicar()
        self.assertEqual(self.aplicar()["estado"], "ja_aplicada")
        for oferta in [self.oferta, replace(self.oferta, turma_codigo="03")]:
            turma = salvar_oferta(self.db, oferta, "673")
            self.assertEqual([p.id for p in turma.professores], [self.destino.id])
        self.assertEqual(len(professores.listar(self.db)), 1)
        self.assertEqual(self.db.scalar(select(func.count(Professor.id))), 2)

    def test_lindomar_tres_disciplinas_duas_unidades_e_reimportacao(self):
        nome = "LINDOMAR BOMFIM DE CARVALHO DE JESUS"
        ofertas = [
            ("IFD0171", "FISICA 1", "178581", "524", "INSTITUTO DE FÍSICA - BRASÍLIA"),
            ("FGA0108", "MATEMÁTICA DISCRETA 2", "180070", "673", "CAMPUS UNB GAMA"),
            (
                "FGA0134",
                "TÓPICOS ESPECIAIS DE ENGENHARIA DE SOFTWARE",
                "188384",
                "673",
                "CAMPUS UNB GAMA",
            ),
        ]
        turmas = []
        for codigo, materia, componente_id, unidade, unidade_nome in ofertas:
            oferta = replace(
                self.oferta,
                componente_codigo=codigo,
                componente_nome=materia,
                componente_id=componente_id,
                unidade_id=unidade,
                docentes=(nome,),
            )
            turma = salvar_oferta(self.db, oferta, unidade, unidade_nome)
            turmas.append((oferta, unidade, unidade_nome, turma.professores[0].id))
        self.db.commit()
        ids = [item[3] for item in turmas]
        destino = ids[0]
        self.assertEqual(len(professores.listar(self.db, nome)), 3)
        self.assertEqual(planejar_grupo(self.db, ids[1:], destino)["colisoes"], 0)
        self.assertEqual(
            aplicar_grupo(self.db, ids[1:], destino, "Fixture do relato do PO")["estado"],
            "aplicada",
        )
        self.db.commit()
        self.db.expire_all()
        self.assertEqual([p.id for p in professores.listar(self.db, nome)], [destino])
        for professor_id in ids:
            self.assertEqual(
                institucional_service.obter_professor(self.db, professor_id).id, destino
            )
            disciplinas = institucional_service.listar_disciplinas_do_professor(
                self.db, professor_id
            )
            self.assertEqual({d.codigo for d in disciplinas}, {item[0] for item in ofertas})
            self.assertEqual({d.departamento for d in disciplinas}, {"524", "673"})
            self.assertTrue(all(d.departamento_nome for d in disciplinas))
        for oferta, unidade, unidade_nome, _ in turmas:
            turma = salvar_oferta(self.db, oferta, unidade, unidade_nome)
            self.assertEqual([p.id for p in turma.professores], [destino])
            comparacao = comparar_professores_da_disciplina(
                turma.disciplina_id, self.db, "recomendacao"
            )
            self.assertEqual([p.professor_id for p in comparacao.professores], [destino])
        self.db.commit()
        self.assertEqual(
            aplicar_grupo(self.db, ids[1:], destino, "Repetição")["estado"], "ja_aplicada"
        )
        self.assertEqual(len(professores.listar(self.db, nome)), 1)
        # Uma ocorrência ainda não confirmada de outro semestre permanece distinta.
        salvar_oferta(self.db, replace(turmas[0][0], periodo="2027.1"), "524")
        self.db.commit()
        self.assertEqual(len(professores.listar(self.db, nome)), 2)

    def test_grupo_colisao_entre_origens_recusa_todas(self):
        terceira = salvar_oferta(
            self.db, replace(self.oferta, turma_codigo="04"), "673"
        ).professores[0]
        self.db.commit()
        primeira = self.avaliar(self.origem)
        self.avaliar(self.destino, primeira.usuario)
        origens = [self.origem.id, self.destino.id]
        self.assertEqual(planejar_grupo(self.db, origens, terceira.id)["colisoes"], 1)
        with self.assertRaises(ReconciliacaoRecusada):
            aplicar_grupo(self.db, origens, terceira.id, "Fixture")
        self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count(ProfessorCorrespondencia.origem_id))), 0)
        self.assertEqual(self.db.scalar(select(func.count(Avaliacao.id))), 2)
        self.assertEqual([p.id for p in self.t1.professores], [self.origem.id])

    def test_falha_na_segunda_origem_desfaz_o_grupo_inteiro(self):
        terceira = salvar_oferta(
            self.db, replace(self.oferta, turma_codigo="04"), "673"
        ).professores[0]
        self.db.commit()
        original = aplicar

        def falhar_na_segunda(db, origem_id, destino_id, evidencia):
            if origem_id == self.destino.id:
                raise RuntimeError("Falha simulada na segunda origem")
            return original(db, origem_id, destino_id, evidencia)

        with patch(
            "app.repositories.reconciliacao_professor_repository.aplicar",
            side_effect=falhar_na_segunda,
        ):
            with self.assertRaisesRegex(RuntimeError, "segunda origem"):
                aplicar_grupo(self.db, [self.origem.id, self.destino.id], terceira.id, "Fixture")
        self.db.expire_all()
        self.assertEqual(self.db.scalar(select(func.count(ProfessorCorrespondencia.origem_id))), 0)
        self.assertEqual([p.id for p in self.t1.professores], [self.origem.id])
        self.assertEqual([p.id for p in self.t2.professores], [self.destino.id])

    def test_grupo_recusa_lista_vazia_repetida_e_destino_como_origem(self):
        for origens in [[], [self.origem.id, self.origem.id], [self.destino.id]]:
            with self.assertRaises(ReconciliacaoRecusada):
                planejar_grupo(self.db, origens, self.destino.id)

    def test_cli_simula_multiplas_origens_sem_alterar_dados(self):
        terceira = salvar_oferta(
            self.db, replace(self.oferta, turma_codigo="04"), "673"
        ).professores[0]
        self.db.commit()
        argumentos = [
            "reconciliar_professores",
            "--origem",
            str(self.origem.id),
            "--origem",
            str(self.destino.id),
            "--destino",
            str(terceira.id),
        ]
        saida = io.StringIO()
        with (
            patch("sys.argv", argumentos),
            patch.object(reconciliar_professores, "SessionLocal", return_value=self.db),
            redirect_stdout(saida),
        ):
            reconciliar_professores.main()
        plano = json.loads(saida.getvalue())
        self.assertEqual(plano["estado"], "pronta_para_confirmacao")
        self.assertEqual(len(plano["correspondencias"]), 2)
        self.assertEqual(self.db.scalar(select(func.count(ProfessorCorrespondencia.origem_id))), 0)

    def test_colisao_bloqueia_sem_descartar_ou_escolher_avaliacoes(self):
        primeira = self.avaliar(self.origem)
        self.avaliar(self.destino, primeira.usuario)
        self.assertEqual(planejar(self.db, self.origem.id, self.destino.id)["colisoes"], 1)
        with self.assertRaises(ReconciliacaoRecusada):
            self.aplicar()
        self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count(Avaliacao.id))), 2)
        self.assertEqual(resolver_id(self.db, self.origem.id), self.origem.id)

    def test_rollback_desfaz_toda_operacao(self):
        avaliacao = self.avaliar(self.origem)
        aplicar(self.db, self.origem.id, self.destino.id, "Evidência")
        self.db.rollback()
        self.assertEqual(avaliacao.professor_id, self.origem.id)
        self.assertEqual(resolver_id(self.db, self.origem.id), self.origem.id)
        self.assertEqual([p.id for p in self.t1.professores], [self.origem.id])

    def test_postgres_timeout_de_lock_desfaz_e_permite_nova_tentativa(self):
        if not self.postgres:
            self.skipTest("Exige PostgreSQL descartável undb_207_test.")
        avaliacao = self.avaliar(self.origem)
        origem_id, destino_id = self.origem.id, self.destino.id
        # Um escritor segura a última tabela bloqueada pela manutenção. O timeout
        # deve desfazer também os locks adquiridos antes dela e não mover dados.
        with self.engine.connect() as escritor:
            transacao = escritor.begin()
            try:
                escritor.exec_driver_sql(
                    "LOCK TABLE professor_correspondencias IN ROW EXCLUSIVE MODE"
                )
                with self.assertRaises(OperationalError) as falha:
                    aplicar(self.db, origem_id, destino_id, "Fixture de contenção")
                self.assertEqual(falha.exception.orig.pgcode, "55P03")
                self.db.rollback()
            finally:
                transacao.rollback()
        self.assertEqual(avaliacao.professor_id, origem_id)
        self.assertEqual(resolver_id(self.db, origem_id), origem_id)
        self.assertEqual([p.id for p in self.t1.professores], [origem_id])
        self.assertEqual(self.db.scalar(select(func.count(ProfessorCorrespondencia.origem_id))), 0)
        self.assertEqual(self.aplicar()["estado"], "aplicada")
        self.db.expire_all()
        self.assertEqual(avaliacao.professor_id, destino_id)
        self.assertEqual([p.id for p in self.t1.professores], [destino_id])

    def test_ids_antigos_api_e_limiar_de_privacidade(self):
        self.avaliar(self.origem)
        self.avaliar(self.destino)
        self.aplicar()

        for professor_id in [self.origem.id, self.destino.id]:
            r = consultar_avaliacoes_professor_disciplina(
                professor_id, self.t1.disciplina_id, self.db
            ).model_dump()
            self.assertEqual(r["total_avaliacoes"], 2)
            self.assertFalse(r["dados_suficientes"])
            self.assertNotIn("didatica", r)
        self.avaliar(self.destino)
        r = comparar_professores_da_disciplina(
            self.t1.disciplina_id, self.db, "recomendacao"
        ).model_dump()
        self.assertEqual(len(r["professores"]), 1)
        self.assertTrue(r["professores"][0]["dados_suficientes"])

    def test_recusa_ciclo_retrocesso_destino_inexistente_e_evidencia_vazia(self):
        for origem, destino, evidencia in [
            (self.origem.id, self.origem.id, "x"),
            (self.origem.id, uuid4(), "x"),
            (self.origem.id, self.destino.id, " "),
        ]:
            with self.assertRaises(ReconciliacaoRecusada):
                aplicar(self.db, origem, destino, evidencia)
        self.aplicar()
        with self.assertRaises(ReconciliacaoRecusada):
            aplicar(self.db, self.destino.id, self.origem.id, "x")

    def test_nao_remove_identidade_institucional_confirmada(self):
        self.origem.siape = "1234567"
        self.origem.identidade_confirmada = True
        self.db.commit()
        with self.assertRaises(ReconciliacaoRecusada):
            self.aplicar()

    def test_migration_aditiva_e_downgrade_bloqueado_com_correspondencia(self):
        path = (
            Path(__file__).parents[1] / "alembic/versions/20261107_01_professor_correspondencias.py"
        )
        spec = importlib.util.spec_from_file_location("migration207", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        self.db.rollback()
        with self.engine.begin() as connection:
            ProfessorCorrespondencia.__table__.drop(connection)
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
                migration.downgrade()
                migration.upgrade()
        self.aplicar()
        with self.engine.begin() as connection:
            with Operations.context(MigrationContext.configure(connection)):
                with self.assertRaises(RuntimeError):
                    migration.downgrade()
