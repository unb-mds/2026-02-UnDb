"""#266 bloco 1: contratos do núcleo, sem conectar endpoints do produto."""

import io
import logging
import os
import secrets
import unittest
from dataclasses import replace
from unittest.mock import Mock, patch
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", secrets.token_urlsafe(32))

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core import config
from app.core.dependencia_limite_abuso import (
    AbusoExcedido,
    LimitadorIndisponivel,
    exigir_limite,
    obter_limitador,
)
from app.core.http_errors import abuso_excedido_seguro, limitador_indisponivel_seguro
from app.core.limite_abuso import IdentidadeAbuso, TipoIdentidade, derivar_chave, engine_limitador
from app.core.safe_logging import FormatoSeguro
from app.domain.email import normalizar_email
from app.domain.limite_abuso import (
    FalhaLimite,
    ModoLimite,
    MotivoLimite,
    PoliticaAbuso,
    ResultadoLimite,
    atraso_progressivo,
)
from app.services.limite_abuso_service import LimitadorAbuso, carregar_politica


def politica(**mudancas):
    return replace(PoliticaAbuso("ensaio", 3, 60, 10, 60), **mudancas)


class ContratosLimiteTest(unittest.TestCase):
    def test_normalizacao_pura_preserva_alias_e_nao_valida_existencia(self):
        self.assertEqual(
            normalizar_email("  PESSOA+Alias@ALUNO.UNB.BR \t"), "pessoa+alias@aluno.unb.br"
        )
        self.assertEqual(normalizar_email("nao-e-email"), "nao-e-email")
        self.assertEqual(normalizar_email(""), "")

    def test_hmac_normalizado_separa_operacao_tipo_global_e_segredo(self):
        segredo = secrets.token_urlsafe(32)
        pessoa = IdentidadeAbuso(TipoIdentidade.EMAIL, " PESSOA@ALUNO.UNB.BR ")
        outra = IdentidadeAbuso(TipoIdentidade.EMAIL, "pessoa@aluno.unb.br")
        chave = derivar_chave(segredo, "login", pessoa)
        self.assertEqual(chave, derivar_chave(segredo, "login", outra))
        self.assertEqual(len(chave), 64)
        self.assertNotEqual(chave, derivar_chave(segredo, "cadastro", pessoa))
        self.assertNotEqual(chave, derivar_chave(segredo, "login", None))
        self.assertNotEqual(chave, derivar_chave(secrets.token_urlsafe(32), "login", pessoa))
        self.assertNotIn("pessoa", repr(pessoa))
        token = secrets.token_urlsafe(32)
        identidade_token = IdentidadeAbuso(TipoIdentidade.TOKEN, token)
        self.assertNotEqual(identidade_token.valor, token)
        self.assertNotIn(token, repr(identidade_token))
        self.assertNotEqual(chave, derivar_chave(segredo, "login", identidade_token))
        conta = IdentidadeAbuso(TipoIdentidade.CONTA, str(uuid4()))
        self.assertEqual(len(derivar_chave(segredo, "login", conta)), 64)
        with self.assertRaises(ValueError):
            IdentidadeAbuso("ip", "192.0.2.1")
        with self.assertRaises(ValueError):
            derivar_chave("", "login", pessoa)

    def test_politica_rejeita_configuracao_insegura(self):
        for mudanca in (
            {"quantidade": 0},
            {"quantidade": True},
            {"janela_segundos": -1},
            {"quantidade_global": 0},
            {"modo": "qualquer"},
            {"falha": "qualquer"},
            {"operacao": "valor@aluno.unb.br"},
            {"atraso_apos": -1},
            {"atraso_inicial_segundos": 2, "atraso_maximo_segundos": 1},
        ):
            with self.subTest(mudanca=mudanca), self.assertRaises(ValueError):
                politica(**mudanca)

    def test_atraso_progressivo_limitado_sem_sleep(self):
        p = politica(atraso_apos=2, atraso_inicial_segundos=1, atraso_maximo_segundos=5)
        self.assertEqual([atraso_progressivo(n, p) for n in range(1, 7)], [0, 1, 2, 4, 5, 5])
        self.assertEqual(atraso_progressivo(10**30, p), 5)
        self.assertEqual(atraso_progressivo(100, politica()), 0)

    def test_politicas_so_por_registro_explicito_e_configuracao(self):
        with patch.object(
            config, "ABUSO_POLITICAS", {"login": {"quantidade": 2, "modo": "observe"}}
        ):
            p = carregar_politica("login")
            self.assertEqual(p.quantidade, 2)
            self.assertEqual(p.quantidade_global, config.ABUSO_QUANTIDADE_GLOBAL_PADRAO)
            self.assertEqual(p.modo, ModoLimite.OBSERVE)
            with self.assertRaises(KeyError):
                carregar_politica("nao_registrada")

    def test_falha_fechada_aberta_e_local_sem_expor_identidade(self):
        fabrica = Mock(side_effect=RuntimeError("marcador-privado-nao-publicar"))
        limitador = LimitadorAbuso(fabrica)
        with patch.object(config, "ABUSO_HMAC_SECRET", secrets.token_urlsafe(32)):
            for falha, permitido in (
                (FalhaLimite.FECHAR, False),
                (FalhaLimite.SEGUIR, True),
                (FalhaLimite.LOCAL, False),
            ):
                r = limitador.consumir(politica(falha=falha))
                self.assertEqual(r.permitido, permitido)
                self.assertTrue(r.indisponivel)
                self.assertGreater(r.retry_after, 0)
                self.assertNotIn("privado", repr(r))
            self.assertFalse(limitador.consumir(politica(modo=ModoLimite.OBSERVE)).permitido)

    def test_segredo_ausente_falha_antes_do_banco_e_nao_usa_secret_key(self):
        fabrica = Mock()
        with patch.object(config, "ABUSO_HMAC_SECRET", ""):
            self.assertTrue(LimitadorAbuso(fabrica).consumir(politica()).indisponivel)
        fabrica.assert_not_called()

    def test_engine_recusa_sqlite_e_timeout_zero(self):
        engine_limitador.cache_clear()
        with patch.object(config, "DATABASE_URL", "sqlite://"), self.assertRaises(ValueError):
            engine_limitador()
        with (
            patch.object(config, "DATABASE_URL", "postgresql+psycopg2://localhost/ci"),
            patch.object(config, "ABUSO_STATEMENT_TIMEOUT_MS", 0),
            self.assertRaises(ValueError),
        ):
            engine_limitador()
        engine_limitador.cache_clear()

    def test_logs_omitidos_mesmo_com_excecao_e_extras(self):
        saida = io.StringIO()
        handler = logging.StreamHandler(saida)
        handler.setFormatter(FormatoSeguro("%(message)s"))
        for evento in ("abuso.negado", "abuso.observado", "abuso.indisponivel"):
            registro = logging.LogRecord(
                "app.services.limite_abuso_service", 30, "", 1, evento, (), None
            )
            registro.motivo = "limite_global"
            registro.operacao = "pessoa@aluno.unb.br"
            registro.chave = secrets.token_hex(32)
            handler.handle(registro)
        self.assertIn("abuso.observado motivo=limite_global", saida.getvalue())
        self.assertNotIn("pessoa", saida.getvalue())
        self.assertNotIn(registro.chave, saida.getvalue())


class DependenciaLimiteTest(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.add_exception_handler(AbusoExcedido, abuso_excedido_seguro)
        self.app.add_exception_handler(LimitadorIndisponivel, limitador_indisponivel_seguro)
        self.limitador = Mock(spec=LimitadorAbuso)
        self.app.dependency_overrides[obter_limitador] = lambda: self.limitador
        self.efeitos = []

        @self.app.post("/ensaio", dependencies=[Depends(exigir_limite("ensaio"))])
        def rota():
            self.efeitos.append(True)
            return {"ok": True}

        self.politicas = patch.object(config, "ABUSO_POLITICAS", {"ensaio": {}})
        self.politicas.start()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.politicas.stop()

    def test_429_503_antes_de_efeitos_com_retry_e_sem_detalhes(self):
        for indisponivel, status in ((False, 429), (True, 503)):
            self.limitador.consumir.return_value = ResultadoLimite(
                False,
                7,
                MotivoLimite.INDISPONIVEL if indisponivel else MotivoLimite.GLOBAL,
                indisponivel=indisponivel,
            )
            r = self.client.post("/ensaio")
            self.assertEqual(r.status_code, status)
            self.assertEqual(r.headers["retry-after"], "7")
            self.assertEqual(r.headers["cache-control"], "no-store")
            self.assertEqual(r.headers["referrer-policy"], "no-referrer")
            self.assertNotIn("limite_global", r.text)
        self.assertEqual(self.efeitos, [])

    def test_observe_ou_falha_aberta_preserva_resultado_sem_negar_rota(self):
        self.limitador.consumir.return_value = ResultadoLimite(
            True, 10, MotivoLimite.GLOBAL, excedido=True
        )
        self.assertEqual(self.client.post("/ensaio").status_code, 200)
        self.assertEqual(self.efeitos, [True])

    def test_configuracao_ausente_fecha_sem_consumir(self):
        with patch.object(config, "ABUSO_POLITICAS", {}):
            self.limitador.falha.return_value = ResultadoLimite(
                False, 5, MotivoLimite.INDISPONIVEL, indisponivel=True
            )
            self.assertEqual(self.client.post("/ensaio").status_code, 503)
        self.limitador.consumir.assert_not_called()

    def test_fallback_local_precisa_ser_fornecido_explicitamente(self):
        self.limitador.consumir.return_value = ResultadoLimite(
            False, 5, MotivoLimite.INDISPONIVEL, indisponivel=True, acao_falha=FalhaLimite.LOCAL
        )
        self.assertEqual(self.client.post("/ensaio").status_code, 503)
        fallback = Mock(return_value=ResultadoLimite(True, 0, MotivoLimite.PERMITIDO))
        dependencia = exigir_limite("ensaio", fallback_local=fallback)
        self.assertTrue(dependencia(None, self.limitador).permitido)
        fallback.assert_called_once()
