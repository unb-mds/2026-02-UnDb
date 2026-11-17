"""#266 bloco 1: PostgreSQL real migrado, exclusivamente em banco descartável local/CI."""

import multiprocessing
import os
import secrets
import time
import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import patch

from sqlalchemy import create_engine, delete, func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core import config
from app.core.limite_abuso import IdentidadeAbuso, TipoIdentidade, derivar_chave, engine_limitador
from app.domain.limite_abuso import FalhaLimite, ModoLimite, MotivoLimite, PoliticaAbuso
from app.models.contador_abuso import ContadorAbuso
from app.services.limite_abuso_service import LimitadorAbuso


def engine_ensaio(url, *, timeouts=None, **opcoes):
    return create_engine(
        url,
        hide_parameters=True,
        connect_args={
            "connect_timeout": 2,
            "options": timeouts or "-c statement_timeout=1000 -c lock_timeout=200",
        },
        **opcoes,
    )


def consumir_em_outro_processo(argumentos):
    url, segredo, politica = argumentos
    config.ABUSO_HMAC_SECRET = segredo
    engine = engine_ensaio(url)
    try:
        servico = LimitadorAbuso(lambda: Session(engine))
        identidade = IdentidadeAbuso(TipoIdentidade.EMAIL, "concorrencia@aluno.unb.br")
        resultados = [servico.consumir(politica, identidade) for _ in range(10)]
        return sum(r.permitido for r in resultados), sum(r.indisponivel for r in resultados)
    finally:
        engine.dispose()


@unittest.skipUnless(
    os.environ.get("ABUSO_POSTGRES_TEST_URL"), "Exige PostgreSQL descartável migrado."
)
class LimitadorPostgresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = os.environ["ABUSO_POSTGRES_TEST_URL"]
        url = make_url(cls.url)
        if (
            url.drivername != "postgresql+psycopg2"
            or url.host not in {"localhost", "127.0.0.1", "::1"}
            or url.database not in {"undb_266_test", "ci"}
        ):
            raise ValueError("Usar somente PostgreSQL descartável local undb_266_test ou CI ci.")
        cls.engine = engine_ensaio(cls.url, pool_size=10, max_overflow=0)
        with cls.engine.connect() as conn:
            persistencia = conn.scalar(
                text(
                    "SELECT relpersistence FROM pg_class WHERE oid=to_regclass('contadores_abuso')"
                )
            )
            if persistencia != "u":
                raise AssertionError("Aplicar a migration UNLOGGED antes da integração.")

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        self.agora = datetime.now(timezone.utc)
        self.operacao = "ensaio_" + uuid4().hex
        self.politica = PoliticaAbuso(self.operacao, 3, 60, 1000, 60)
        self.segredo = secrets.token_urlsafe(32)
        self.secret_patch = patch.object(config, "ABUSO_HMAC_SECRET", self.segredo)
        self.secret_patch.start()
        self.identidade = IdentidadeAbuso(TipoIdentidade.EMAIL, "ensaio@aluno.unb.br")
        self.limitador = LimitadorAbuso(lambda: Session(self.engine), lambda db: self.agora)

    def tearDown(self):
        self.secret_patch.stop()
        with Session(self.engine) as db, db.begin():
            db.execute(delete(ContadorAbuso).where(ContadorAbuso.operacao == self.operacao))

    def linhas(self):
        with Session(self.engine) as db:
            return list(
                db.scalars(select(ContadorAbuso).where(ContadorAbuso.operacao == self.operacao))
            )

    def test_migration_unlogged_e_contadores_nao_guardam_dados_abertos(self):
        self.assertTrue(self.limitador.consumir(self.politica, self.identidade).permitido)
        linhas = self.linhas()
        self.assertEqual(len(linhas), 2)
        self.assertTrue(all(len(linha.chave) == 64 for linha in linhas))
        self.assertTrue(all("ensaio@" not in linha.chave for linha in linhas))

    def test_engine_real_do_nucleo_aplica_timeouts_e_papel_de_aplicacao(self):
        engine_limitador.cache_clear()
        with patch.object(config, "DATABASE_URL", self.url):
            engine = engine_limitador()
            try:
                with engine.connect() as conn:
                    self.assertEqual(conn.scalar(text("SHOW statement_timeout")), "250ms")
                    self.assertEqual(conn.scalar(text("SHOW lock_timeout")), "100ms")
                self.assertTrue(LimitadorAbuso().consumir(self.politica, self.identidade).permitido)
            finally:
                engine.dispose()
                engine_limitador.cache_clear()

    def test_incremento_atomico_concorrente_sem_perda_ou_excesso_de_permissoes(self):
        p = replace(self.politica, quantidade=7)
        # Atomicidade é distinta do orçamento de tempo sob contenção no host.
        # Os testes de timeout continuam usando os limites curtos específicos.
        isolado = engine_ensaio(
            self.url,
            pool_size=8,
            max_overflow=0,
            timeouts="-c statement_timeout=10000 -c lock_timeout=5000",
        )
        limitador = LimitadorAbuso(lambda: Session(isolado), lambda db: self.agora)
        try:
            with ThreadPoolExecutor(max_workers=8) as pool:
                resultados = list(
                    pool.map(lambda _: limitador.consumir(p, self.identidade), range(40))
                )
        finally:
            isolado.dispose()
        self.assertEqual(sum(r.permitido for r in resultados), 7)
        self.assertFalse(any(r.indisponivel for r in resultados))
        self.assertEqual(sorted(linha.quantidade for linha in self.linhas()), [40, 40])

    def test_estado_compartilhado_entre_processos_e_novas_conexoes(self):
        p = replace(self.politica, quantidade=7)
        argumentos = (self.url, self.segredo, p)
        with ProcessPoolExecutor(
            max_workers=2, mp_context=multiprocessing.get_context("spawn")
        ) as pool:
            resultados = list(pool.map(consumir_em_outro_processo, [argumentos, argumentos]))
        self.assertEqual(sum(permitidos for permitidos, _ in resultados), 7)
        self.assertEqual(sum(falhas for _, falhas in resultados), 0)
        outro = engine_ensaio(self.url)
        try:
            resultado = LimitadorAbuso(lambda: Session(outro)).consumir(
                p, IdentidadeAbuso(TipoIdentidade.EMAIL, "concorrencia@aluno.unb.br")
            )
            self.assertFalse(resultado.permitido)
            self.assertFalse(resultado.indisponivel)
        finally:
            outro.dispose()

    def test_capacidade_global_independe_de_troca_de_token_ou_ausencia_de_identidade(self):
        p = replace(self.politica, quantidade_global=2)
        for _ in range(2):
            identidade = IdentidadeAbuso(TipoIdentidade.TOKEN, secrets.token_urlsafe(32))
            self.assertTrue(self.limitador.consumir(p, identidade).permitido)
        r = self.limitador.consumir(p)
        self.assertFalse(r.permitido)
        self.assertEqual(r.motivo, MotivoLimite.GLOBAL)
        self.assertEqual(r.retry_after, 60)
        self.assertEqual(len(self.linhas()), 3)  # Não cria identidade após exceder global.

    def test_expiracao_no_limite_exato_independe_da_purga(self):
        p = replace(self.politica, quantidade=1)
        self.assertTrue(self.limitador.consumir(p, self.identidade).permitido)
        self.agora += timedelta(seconds=59, microseconds=500000)
        r = self.limitador.consumir(p, self.identidade)
        self.assertFalse(r.permitido)
        self.assertEqual(r.retry_after, 1)
        self.agora += timedelta(microseconds=500000)
        self.assertTrue(self.limitador.consumir(p, self.identidade).permitido)
        self.assertEqual(sorted(linha.quantidade for linha in self.linhas()), [1, 1])

    def test_janelas_global_e_individual_independentes(self):
        p = replace(self.politica, quantidade=1, janela_global_segundos=10)
        self.limitador.consumir(p, self.identidade)
        self.agora += timedelta(seconds=10)
        r = self.limitador.consumir(p, self.identidade)
        self.assertFalse(r.permitido)
        self.assertEqual(r.motivo, MotivoLimite.IDENTIDADE)
        self.assertEqual(r.retry_after, 50)

    def test_janela_calendario_reseta_na_meia_noite_utc(self):
        self.agora = self.agora.replace(hour=23, minute=59, second=59, microsecond=0)
        dia = int(timedelta(days=1).total_seconds())
        p = replace(
            self.politica,
            quantidade_global=2,
            janela_segundos=dia,
            janela_global_segundos=dia,
            alinhar_janela_utc=True,
        )
        self.assertTrue(self.limitador.consumir(p).permitido)
        self.assertTrue(self.limitador.consumir(p).permitido)
        negado = self.limitador.consumir(p)
        self.assertFalse(negado.permitido)
        self.assertEqual(negado.retry_after, 1)
        self.agora += timedelta(seconds=1)
        self.assertTrue(self.limitador.consumir(p).permitido)
        self.assertEqual(self.linhas()[0].quantidade, 1)

    def test_observe_registra_excesso_mas_nao_nega(self):
        p = replace(self.politica, quantidade=1, modo=ModoLimite.OBSERVE)
        self.limitador.consumir(p, self.identidade)
        with self.assertLogs("app.services.limite_abuso_service", level="WARNING") as logs:
            r = self.limitador.consumir(p, self.identidade)
        self.assertTrue(r.permitido)
        self.assertTrue(r.excedido)
        self.assertEqual(r.motivo, MotivoLimite.IDENTIDADE)
        self.assertIn("abuso.observado", logs.output[0])
        self.assertNotIn(self.identidade.valor, str(logs.output))

    def test_atraso_progressivo_nao_e_estendido_por_tentativas_na_espera(self):
        p = replace(
            self.politica,
            quantidade=100,
            atraso_apos=1,
            atraso_inicial_segundos=1,
            atraso_maximo_segundos=4,
        )
        self.assertTrue(self.limitador.consumir(p, self.identidade).permitido)
        self.assertEqual(self.limitador.consumir(p, self.identidade).retry_after, 1)
        self.agora += timedelta(seconds=1)
        self.assertTrue(self.limitador.consumir(p, self.identidade).permitido)
        self.assertEqual(self.limitador.consumir(p, self.identidade).retry_after, 2)
        self.agora += timedelta(seconds=2)
        self.assertTrue(self.limitador.consumir(p, self.identidade).permitido)
        self.assertEqual(self.limitador.consumir(p, self.identidade).retry_after, 4)
        self.agora += timedelta(seconds=3)
        self.assertEqual(self.limitador.consumir(p, self.identidade).retry_after, 1)
        self.agora += timedelta(seconds=1)
        self.assertTrue(self.limitador.consumir(p, self.identidade).permitido)

    def test_observe_nao_instala_espera_progressiva(self):
        p = replace(
            self.politica,
            quantidade=100,
            modo=ModoLimite.OBSERVE,
            atraso_apos=1,
            atraso_inicial_segundos=1,
            atraso_maximo_segundos=4,
        )
        for _ in range(3):
            self.assertTrue(self.limitador.consumir(p, self.identidade).permitido)
        chave = derivar_chave(self.segredo, self.operacao, self.identidade)
        linha = next(linha for linha in self.linhas() if linha.chave == chave)
        self.assertEqual(linha.quantidade, 3)
        self.assertIsNone(linha.proxima_tentativa_em)

    def test_reiniciar_identidade_nao_reinicia_global(self):
        self.limitador.consumir(self.politica, self.identidade)
        self.assertTrue(self.limitador.reiniciar_identidade(self.politica, self.identidade))
        self.limitador.consumir(self.politica, self.identidade)
        self.assertEqual(sorted(linha.quantidade for linha in self.linhas()), [1, 2])

    def test_troca_para_observe_conta_tentativas_mesmo_com_espera_anterior(self):
        p = replace(
            self.politica,
            quantidade=100,
            atraso_apos=1,
            atraso_inicial_segundos=1,
            atraso_maximo_segundos=4,
        )
        self.limitador.consumir(p, self.identidade)
        for _ in range(3):
            self.assertTrue(
                self.limitador.consumir(
                    replace(p, modo=ModoLimite.OBSERVE), self.identidade
                ).permitido
            )
        chave = derivar_chave(self.segredo, self.operacao, self.identidade)
        self.assertEqual(
            next(linha.quantidade for linha in self.linhas() if linha.chave == chave), 4
        )

    def test_contador_confirmado_independe_do_rollback_do_chamador(self):
        with Session(self.engine) as db:
            db.execute(select(func.now()))
            self.limitador.consumir(self.politica, self.identidade)
            db.rollback()
        self.assertEqual(len(self.linhas()), 2)

    def test_falha_no_segundo_incremento_reverte_global(self):
        from app.repositories import limite_abuso_repository as repo

        original = repo.incrementar
        chamadas = []

        def incrementar(*args, **kwargs):
            chamadas.append(True)
            if len(chamadas) == 2:
                raise RuntimeError("falha sintética")
            return original(*args, **kwargs)

        with patch.object(repo, "incrementar", side_effect=incrementar):
            self.assertTrue(self.limitador.consumir(self.politica, self.identidade).indisponivel)
        self.assertEqual(self.linhas(), [])

    def test_lock_timeout_real_gera_falha_fechada_ou_aberta_sem_espera_longa(self):
        self.limitador.consumir(self.politica)
        chave = derivar_chave(self.segredo, self.operacao, None)
        with Session(self.engine) as bloqueio, bloqueio.begin():
            bloqueio.execute(
                select(ContadorAbuso)
                .where(ContadorAbuso.operacao == self.operacao, ContadorAbuso.chave == chave)
                .with_for_update()
            )
            inicio = time.monotonic()
            fechado = self.limitador.consumir(self.politica)
            aberto = self.limitador.consumir(replace(self.politica, falha=FalhaLimite.SEGUIR))
            self.assertTrue(fechado.indisponivel)
            self.assertFalse(fechado.permitido)
            self.assertTrue(aberto.indisponivel)
            self.assertTrue(aberto.permitido)
            self.assertLess(time.monotonic() - inicio, 3)
        self.assertEqual(self.linhas()[0].quantidade, 1)

    def test_statement_timeout_real(self):
        def relogio(db):
            db.execute(text("SELECT pg_sleep(2)"))
            return self.agora

        inicio = time.monotonic()
        r = LimitadorAbuso(lambda: Session(self.engine), relogio).consumir(self.politica)
        self.assertTrue(r.indisponivel)
        self.assertLess(time.monotonic() - inicio, 3)
        self.assertEqual(self.linhas(), [])

    def test_pool_timeout_real(self):
        engine = engine_ensaio(self.url, pool_size=1, max_overflow=0, pool_timeout=0.05)
        try:
            with engine.connect():
                r = LimitadorAbuso(lambda: Session(engine)).consumir(self.politica)
                self.assertTrue(r.indisponivel)
        finally:
            engine.dispose()

    def test_limpeza_em_lotes_idempotente_e_sem_apagar_ativos(self):
        self.limitador.consumir(self.politica, self.identidade)
        self.agora += timedelta(seconds=60)
        self.limitador.consumir(replace(self.politica, operacao=self.operacao + "a"))
        try:
            with patch.object(config, "ABUSO_LIMPEZA_LOTE", 1):
                self.assertEqual(self.limitador.limpar_expirados(), 1)
                self.assertEqual(self.limitador.limpar_expirados(), 1)
                self.assertEqual(self.limitador.limpar_expirados(), 0)
            self.assertEqual(self.linhas(), [])
        finally:
            with Session(self.engine) as db, db.begin():
                db.execute(
                    delete(ContadorAbuso).where(ContadorAbuso.operacao == self.operacao + "a")
                )

    def test_limpeza_nao_aguarda_expirado_bloqueado(self):
        self.limitador.consumir(self.politica)
        self.agora += timedelta(seconds=60)
        with Session(self.engine) as bloqueio, bloqueio.begin():
            bloqueio.execute(
                select(ContadorAbuso)
                .where(ContadorAbuso.operacao == self.operacao)
                .with_for_update()
            )
            self.assertEqual(self.limitador.limpar_expirados(), 0)
        self.assertEqual(self.limitador.limpar_expirados(), 1)
