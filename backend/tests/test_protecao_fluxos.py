"""#266 Bloco 3: matriz aprovada, bloqueio antes de efeitos e exceções autorizadas."""

import os
import secrets
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from fastapi.testclient import TestClient
from app.core import config, protecao_fluxos as guard
from app.core.auth import obter_usuario_confirmado, obter_moderador, obter_sessao_opcional
from app.core.database import get_db
from app.core.dependencia_limite_abuso import obter_limitador, AbusoExcedido, LimitadorIndisponivel
from app.domain.limite_abuso import MotivoLimite, ResultadoLimite
from app.main import app
from app.routers import avaliacoes, denuncias, moderacao

from tests import test_auth_abuso_postgres as pg_fixture
from app.services.limite_abuso_service import LimitadorAbuso
from sqlalchemy.orm import Session
from sqlalchemy import delete
from app.models.contador_abuso import ContadorAbuso


class FluxosTest(unittest.TestCase):
    def setUp(self):
        self.usuario = SimpleNamespace(id=uuid4(), moderador=True, email_confirmado=True)
        self.lim = Mock()
        self.lim.consumir.return_value = ResultadoLimite(
            False, 17, MotivoLimite.GLOBAL, excedido=True
        )
        self.anterior = dict(app.dependency_overrides)
        app.dependency_overrides.update(
            {
                get_db: lambda: None,
                obter_usuario_confirmado: lambda: self.usuario,
                obter_moderador: lambda: self.usuario,
                obter_sessao_opcional: lambda: None,
                obter_limitador: lambda: self.lim,
            }
        )
        self.client = TestClient(app, headers={"Origin": config.CORS_ORIGINS[0]})

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.anterior)

    def test_matriz_excesso_e_falha(self):
        for op in config.FLUXOS_ABUSO_POLITICAS:
            with self.subTest(op=op):
                with self.assertRaises(AbusoExcedido):
                    guard.verificar(op, self.usuario, self.lim)
                self.lim.consumir.return_value = ResultadoLimite(
                    False, 5, MotivoLimite.INDISPONIVEL, indisponivel=True
                )
                falha = config.FLUXOS_ABUSO_POLITICAS[op]["falha"]
                with patch.object(guard, "fallback_denuncia") as fallback:
                    if falha == "fechar":
                        with self.assertRaises(LimitadorIndisponivel):
                            guard.verificar(op, self.usuario, self.lim)
                    else:
                        guard.verificar(op, self.usuario, self.lim)
                    self.assertEqual(fallback.called, falha == "local")
                self.lim.consumir.return_value = ResultadoLimite(
                    False, 17, MotivoLimite.GLOBAL, excedido=True
                )

    def test_fallback_global_limitado_e_expira(self):
        with (
            patch.object(guard, "_inicio", 100),
            patch.object(guard, "_quantidade", 0),
            patch.object(guard, "monotonic", return_value=100) as clock,
        ):
            for _ in range(config.DENUNCIA_FALLBACK_QUANTIDADE):
                guard.fallback_denuncia()
            with self.assertRaises(AbusoExcedido) as erro:
                guard.fallback_denuncia()
            self.assertEqual(erro.exception.retry_after, config.DENUNCIA_FALLBACK_JANELA_SEGUNDOS)
            clock.return_value += config.DENUNCIA_FALLBACK_JANELA_SEGUNDOS
            guard.fallback_denuncia()

    def test_papeis_conta_sem_elevacao_na_avaliacao(self):
        self.lim.consumir.return_value = ResultadoLimite(True, 0, MotivoLimite.PERMITIDO)
        guard.avaliar(self.usuario, self.lim)
        politica, identidade = self.lim.consumir.call_args.args
        self.assertEqual(politica.operacao, "avaliacao.escrever")
        self.assertEqual(identidade.valor, str(self.usuario.id))
        guard.moderar("identidade.fila")(self.usuario, self.lim)
        self.assertEqual(
            self.lim.consumir.call_args.args[0].operacao, "identidade.fila.reconciliador"
        )
        for papel in ("moderador", "reconciliador"):
            p = guard.politica_fluxo("moderacao.fila", papel)
            self.assertGreater(p.quantidade, politica.quantidade)
            self.assertTrue(p.operacao.endswith(papel))

    def test_denuncia_anonima_global_sem_ip(self):
        with patch.object(denuncias.denuncia_service, "registrar") as escrever:
            r = self.client.post(
                f"/api/comentarios/{uuid4()}/denuncias",
                json={"motivo": "SPAM"},
                headers={"X-Forwarded-For": "192.0.2.1"},
            )
        self.assertEqual(r.status_code, 429)
        self.assertEqual(r.headers["retry-after"], "17")
        self.assertIn("retry-after", r.headers["access-control-expose-headers"].lower())
        escrever.assert_not_called()
        self.assertIsNone(self.lim.consumir.call_args.args[1])

    def test_avaliacao_sem_escrita_quando_negada(self):
        dados = {
            "professor_id": str(uuid4()),
            "disciplina_id": str(uuid4()),
            "didatica": 3,
            "dificuldade": "MEDIO",
            "chamada": False,
            "disponibiliza_material": False,
            "qualidade_material": None,
            "recomenda": True,
        }
        with patch.object(avaliacoes.avaliacao_service, "registrar_avaliacao") as escrever:
            r = self.client.post("/api/avaliacoes", json=dados)
        self.assertEqual(r.status_code, 429)
        escrever.assert_not_called()

    def test_fila_sem_bypass_e_remocao_urgente_isenta(self):
        self.assertEqual(self.client.get("/api/moderacao/comentarios").status_code, 429)
        self.lim.reset_mock()
        with patch.object(
            moderacao.moderacao_service,
            "decidir",
            side_effect=moderacao.moderacao_service.ModeracaoError(404, "ausente"),
        ) as decidir:
            r = self.client.post(
                f"/api/moderacao/comentarios/{uuid4()}/acoes",
                json={"acao": "REMOVER", "motivo": "SPAM"},
            )
        self.assertEqual(r.status_code, 404)
        decidir.assert_called_once()
        self.lim.consumir.assert_not_called()

    def test_canal_compartilhado_e_leituras_publicas_livres(self):
        for rota, dados in [
            (
                "",
                {
                    "categoria": "OUTRA",
                    "alvo": "ensaio",
                    "descricao": "Pedido sintetico",
                    "evidencia": "ensaio",
                },
            ),
            ("/consultar", {"protocolo": str(uuid4()), "chave": "x" * 43}),
            ("/complementos", {"protocolo": str(uuid4()), "chave": "x" * 43, "texto": "ensaio"}),
        ]:
            r = self.client.post("/api/solicitacoes" + rota, json=dados)
            self.assertEqual(r.status_code, 429)
        self.lim.reset_mock()
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/api/solicitacoes/disponibilidade").status_code, 200)
        self.lim.consumir.assert_not_called()


@unittest.skipUnless(
    os.environ.get("ABUSO_POSTGRES_TEST_URL"), "Exige PostgreSQL descartável migrado."
)
class FluxosPostgresTest(unittest.TestCase):
    setUpClass = classmethod(pg_fixture.AuthAbusoPostgresTest.setUpClass.__func__)
    tearDownClass = classmethod(pg_fixture.AuthAbusoPostgresTest.tearDownClass.__func__)

    def test_instancias_compartilham_orcamento_e_observe(self):
        op = "titular.consultar"
        with (
            patch.object(config, "ABUSO_HMAC_SECRET", secrets.token_urlsafe(32)),
            patch.object(config, "ABUSO_POLITICAS", {op: {"quantidade_global": 1}}),
        ):
            primeiro = LimitadorAbuso(lambda: Session(self.pg_engine))
            segundo = LimitadorAbuso(lambda: Session(self.pg_engine))
            try:
                guard.verificar(op, None, primeiro)
                with self.assertRaises(AbusoExcedido):
                    guard.verificar(op, None, segundo)
                config.ABUSO_POLITICAS[op]["modo"] = "observe"
                guard.verificar(op, None, segundo)
            finally:
                with Session(self.pg_engine) as db, db.begin():
                    db.execute(delete(ContadorAbuso).where(ContadorAbuso.operacao == op))
