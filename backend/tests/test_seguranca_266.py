"""#266: fronteiras HTTP/logs e limitações do orçamento, somente dados sintéticos."""

import logging
import asyncio
import os
import sys
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.responses import Response
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from starlette.requests import Request
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.core import config, limite_atendimento
from app.core.auth import definir_cookie_sessao, remover_cookie_sessao
from app.core.database import Base, engine, get_db
from app.core.security import gerar_hash_senha
from app.models.usuario import Usuario
from app.core.safe_logging import FormatoSeguro
from app.main import app, proteger_cache_privado
from app.schemas.auth import LoginRequest
from app.services import auth_service
from app.services.email_service import ConsoleEmailSender, EmailDeliveryError, ResendEmailSender
from tests import test_auth as auth_tests


class FronteiraHttpTest(unittest.TestCase):
    def setUp(self):
        self.override = dict(app.dependency_overrides)
        app.dependency_overrides[get_db] = lambda: None
        self.client = TestClient(app, raise_server_exceptions=False)
        self.flags = patch.object(config, "CORS_ORIGINS", ["https://frontend.example"])
        self.flags.start()

    def tearDown(self):
        self.client.close()
        self.flags.stop()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.override)
        limite_atendimento._janelas.clear()

    def test_mutacoes_rejeitadas_antes_de_efeitos(self):
        headers = [
            {"Origin": "https://externa.example"},
            {"Origin": "null"},
            {"Origin": "https://frontend.example.externa.example"},
            {"Origin": "https://frontend.example/caminho"},
            {"Origin": "https://frontend.example:invalido"},
            {"Origin": "https://usuario@frontend.example"},
            {"Origin": "https://frontend.example, https://externa.example"},
            [("Origin", "https://frontend.example"), ("Origin", "https://externa.example")],
            {"Referer": "https://externa.example/"},
        ]
        with patch.object(auth_service, "autenticar") as autenticar:
            for cabecalhos in headers:
                r = self.client.post("/api/auth/login", json={}, headers=cabecalhos)
                self.assertEqual(r.status_code, 403)
                self.assertEqual(r.headers["cache-control"], "no-store")
                self.assertNotIn("frontend.example", r.text)
            autenticar.assert_not_called()
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            r = self.client.request(method, "/api/atendimento", headers=headers[0])
            self.assertEqual(r.status_code, 403)

    def test_origem_legitima_referencia_e_preflight(self):
        for headers in (
            {"Origin": "https://frontend.example"},
            {"Referer": "https://frontend.example/contato?token=sintetico"},
            {"Referer": "https://frontend.example/confirmar-email?returnTo=%2Fprofessores"},
        ):
            r = self.client.post("/api/auth/login", json={}, headers=headers)
            self.assertEqual(r.status_code, 422)  # Chegou ao contrato normal.
        r = self.client.options(
            "/api/auth/login",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(r.status_code, 200)  # Lista CORS carregada ao construir o app.

    def test_ausencia_de_metadados_e_prioridade_de_origin(self):
        self.assertEqual(self.client.post("/api/auth/login", json={}).status_code, 403)
        self.assertEqual(self.client.post("/api/auth/login/", json={}).status_code, 403)
        self.assertEqual(self.client.post("/api/auth/confirmar", json={}).status_code, 422)
        for path in ("/api/auth/logout", "/api/avaliacoes", "/api/solicitacoes/complementos"):
            r = self.client.post(path, json={}, headers={"Cookie": "undb_session=sintetico"})
            self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.get("/health").status_code, 200)
        r = self.client.post(
            "/api/auth/login",
            json={},
            headers={"Origin": "null", "Referer": "https://frontend.example/"},
        )
        self.assertEqual(r.status_code, 403)

    def test_validacao_nao_reflete_valores_contextos_ou_campos_extras(self):
        marcador = "dado-privado-sintetico-266"
        casos = [
            ("/api/auth/redefinir-senha", {"token": marcador, "senha": marcador * 20}),
            ("/api/solicitacoes/consultar", {"protocolo": marcador, "chave": marcador}),
            ("/api/solicitacoes/complementos", {marcador: marcador, "texto": marcador}),
            ("/api/auth/cadastro", {"nome": marcador, "email": marcador, "senha": marcador}),
        ]
        for path, body in casos:
            r = self.client.post(path, json=body)
            self.assertEqual(r.status_code, 422)
            self.assertNotIn(marcador, r.text)
            self.assertNotIn('"input"', r.text)
            self.assertNotIn('"ctx"', r.text)
            self.assertEqual(r.headers["cache-control"], "no-store")

    def test_erro_interno_generico_e_provedor_sem_corpo(self):
        marcador = "segredo-provedor-sintetico-266"
        with patch.object(auth_service, "confirmar_email", side_effect=RuntimeError(marcador)):
            with self.assertLogs("app.core.http_errors", level="ERROR") as logs:
                r = self.client.post("/api/auth/confirmar", json={"token": "x" * 43})
        self.assertEqual(r.status_code, 500)
        self.assertNotIn(marcador, r.text + str(logs.output))
        self.assertEqual(r.headers["cache-control"], "no-store")
        with patch(
            "app.services.email_service.resend.Emails.send", side_effect=RuntimeError(marcador)
        ):
            try:
                ResendEmailSender("chave-sintetica", "teste@example.com").enviar_confirmacao(
                    "teste@aluno.unb.br", "https://frontend.example/?token=sintetico"
                )
            except EmailDeliveryError as erro:
                self.assertNotIn(marcador, str(erro))
                registro = logging.LogRecord(
                    "uvicorn.error", 40, __file__, 1, "falha", (), sys.exc_info()
                )
                self.assertNotIn(marcador, FormatoSeguro().format(registro))

    def test_cookie_invalido_e_removido_tambem_na_resposta_401(self):
        with patch.object(
            auth_service,
            "validar_e_renovar_sessao",
            side_effect=auth_service.SessaoInvalidaError("Sessão inválida."),
        ):
            r = self.client.post(
                "/api/auth/logout",
                headers={"Origin": "https://frontend.example", "Cookie": "undb_session=sintetico"},
            )
        self.assertEqual(r.status_code, 401)
        self.assertIn("Max-Age=0", r.headers["set-cookie"])
        self.assertEqual(r.headers["cache-control"], "no-store")

    def test_origem_rejeitada_nao_renova_sessao(self):
        with patch.object(auth_service, "validar_e_renovar_sessao") as validar:
            r = self.client.post(
                "/api/auth/logout",
                headers={"Origin": "https://externa.example", "Cookie": "undb_session=sintetico"},
            )
        self.assertEqual(r.status_code, 403)
        validar.assert_not_called()

    def test_cache_privado_em_erros_de_origem_metodo_e_rota(self):
        for prefixo in (
            "/api/auth",
            "/api/avaliacoes",
            "/api/comentarios",
            "/api/agradecimentos",
            "/api/moderacao",
            "/api/moderacao/identidades",
            "/api/solicitacoes",
            "/api/atendimento",
        ):
            for metodo, sufixo, headers, esperado in (
                ("GET", "/rota-inexistente", {}, 404),
                ("POST", "/rota-inexistente", {"Origin": "null"}, 403),
            ):
                with self.subTest(prefixo=prefixo, metodo=metodo):
                    r = self.client.request(metodo, prefixo + sufixo, headers=headers)
                    self.assertEqual(r.status_code, esperado)
                    self.assertEqual(r.headers["cache-control"], "no-store")
                    self.assertEqual(r.headers["referrer-policy"], "no-referrer")
        for caminho in ("/health", "/api/auth-publico", "/api/moderacao-publica"):
            r = self.client.get(caminho)
            self.assertNotIn("cache-control", r.headers)
            self.assertNotIn("referrer-policy", r.headers)

    def test_cache_preserva_cookies_cors_e_outros_cabecalhos(self):
        async def verificar(caminho):
            resposta = Response(
                headers={
                    "Cache-Control": "public, max-age=60",
                    "Referrer-Policy": "same-origin",
                    "Access-Control-Allow-Origin": "https://frontend.example",
                    "Vary": "Origin",
                }
            )
            resposta.set_cookie("sintetico", "valor", httponly=True)

            async def proximo(request):
                return resposta

            request = Request({"type": "http", "path": caminho, "method": "GET"})
            r = await proteger_cache_privado(request, proximo)
            self.assertIs(r, resposta)
            self.assertIn("sintetico=valor", r.headers["set-cookie"])
            self.assertEqual(r.headers["access-control-allow-origin"], "https://frontend.example")
            self.assertEqual(r.headers["vary"], "Origin")
            return r

        privado = asyncio.run(verificar("/api/comentarios/meu"))
        self.assertEqual(privado.headers["cache-control"], "no-store")
        self.assertEqual(privado.headers["referrer-policy"], "no-referrer")
        publico = asyncio.run(verificar("/health"))
        self.assertEqual(publico.headers["cache-control"], "public, max-age=60")
        self.assertEqual(publico.headers["referrer-policy"], "same-origin")


class LogsTest(unittest.TestCase):
    def test_evento_http_preserva_template_status_e_metodo(self):
        r = logging.LogRecord("app.http", 20, __file__, 1, "http.resposta", (), None)
        r.metodo = "POST"
        r.rota = "/api/atendimento/{protocolo}/eventos"
        r.status_http = 200
        resultado = FormatoSeguro().format(r)
        self.assertIn(r.rota, resultado)
        self.assertIn("POST", resultado)
        self.assertIn("200", resultado)

    def test_erro_de_importacao_nao_persiste_mensagem_bruta(self):
        from app.services.sigaa_import_service import _mensagem_erro

        self.assertNotIn("segredo-sintetico", _mensagem_erro(RuntimeError("segredo-sintetico")))
        self.assertIn("RuntimeError", _mensagem_erro(RuntimeError("segredo-sintetico")))

    def test_access_logs_e_excecoes_nao_expoem_segredos(self):
        segredo = "sintetico-266-segredo"
        records = [
            logging.LogRecord(
                "uvicorn.access",
                20,
                __file__,
                1,
                '%s - "%s %s HTTP/%s" %d',
                ("192.0.2.1:1234", "POST", f"/api/{segredo}?token={segredo}", "1.1", 422),
                None,
            ),
            logging.LogRecord("httpx", 20, __file__, 1, segredo, (), None),
            logging.LogRecord("sqlalchemy.engine", 40, __file__, 1, "params=%s", (segredo,), None),
        ]
        for r in records:
            saida = FormatoSeguro().format(r)
            self.assertNotIn(segredo, saida)
            self.assertNotIn("192.0.2.1", saida)
        self.assertIn("422", FormatoSeguro().format(records[0]))
        self.assertIn(segredo, records[1].msg)  # Não altera registro compartilhado.

    def test_console_somente_local_e_com_dados_sinteticos(self):
        with patch.object(config, "DEBUG", False), self.assertRaises(EmailDeliveryError):
            ConsoleEmailSender().enviar_confirmacao(
                "teste@example.com", "https://example.com/?token=teste"
            )
        with (
            patch.object(config, "DEBUG", True),
            self.assertLogs("app.services.email_service") as logs,
        ):
            ConsoleEmailSender().enviar_confirmacao(
                "teste@example.com", "http://localhost/?token=teste"
            )
        self.assertIn("token=teste", logs.output[0])

    def test_parametros_sql_ocultos_sem_perder_categoria_da_falha(self):
        self.assertTrue(engine.hide_parameters)
        e = create_engine("sqlite://", hide_parameters=True)
        try:
            with e.connect() as conn:
                with self.assertRaises(Exception) as erro:
                    conn.execute(
                        text("select * from tabela_inexistente where id=:id"),
                        {"id": "segredo-sintetico"},
                    )
            self.assertNotIn("segredo-sintetico", str(erro.exception))
            self.assertIn("OperationalError", type(erro.exception).__name__)
        finally:
            e.dispose()


class OrcamentoTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        limite_atendimento._janelas.clear()

    def tearDown(self):
        limite_atendimento._janelas.clear()

    def request(self, cliente="192.0.2.1", headers=()):
        return Request({"type": "http", "client": (cliente, 1234), "headers": list(headers)})

    def test_janela_compartilhamento_reinicio_e_instancias(self):
        with (
            patch.object(config, "CANAL_TITULARES_LIMITE_MINUTO", 1),
            patch.object(limite_atendimento, "monotonic", return_value=100) as relogio,
        ):
            limite_atendimento.limitar(self.request())
            with self.assertRaises(HTTPException) as erro:
                limite_atendimento.limitar(
                    self.request(headers=[(b"x-forwarded-for", b"192.0.2.2")])
                )
            self.assertEqual(erro.exception.status_code, 429)
            limite_atendimento.limitar(self.request("192.0.2.2"))
            self.assertTrue(all(len(k) == 64 for k in limite_atendimento._janelas))
            relogio.return_value = 160
            limite_atendimento.limitar(self.request())
            # Outro estado de processo e reinício recebem orçamento novo: limitação confirmada.
            with patch.object(limite_atendimento, "_janelas", {}):
                limite_atendimento.limitar(self.request())
            limite_atendimento._janelas.clear()
            limite_atendimento.limitar(self.request())

    async def test_cabecalhos_so_alteram_cliente_se_peer_e_confiavel_no_servidor(self):
        clientes = []

        async def destino(scope, receive, send):
            clientes.append(scope["client"][0])

        scope = {
            "type": "http",
            "scheme": "http",
            "client": ("192.0.2.10", 1234),
            "headers": [(b"x-forwarded-for", b"198.51.100.1")],
        }
        await ProxyHeadersMiddleware(destino, trusted_hosts=["127.0.0.1"])(dict(scope), None, None)
        await ProxyHeadersMiddleware(destino, trusted_hosts=["192.0.2.10"])(dict(scope), None, None)
        self.assertEqual(clientes, ["192.0.2.10", "198.51.100.1"])


class PrazosTest(unittest.TestCase):
    setUp = auth_tests.AuthServiceTest.setUp
    tearDown = auth_tests.AuthServiceTest.tearDown
    _criar_usuario = auth_tests.AuthServiceTest._criar_usuario

    def test_limite_exato_de_expiracao_com_relogio_controlado(self):
        agora = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self._criar_usuario()
        with patch.object(auth_service, "_agora_utc", return_value=agora):
            login = auth_service.autenticar(
                self.db, LoginRequest(email=self.dados.email, senha=self.dados.senha)
            )
        with patch.object(auth_service, "_agora_utc", return_value=agora + timedelta(days=7)):
            with self.assertRaises(auth_service.SessaoInvalidaError):
                auth_service.validar_e_renovar_sessao(self.db, login.token)

    def test_cookie_seguro_em_producao_e_local(self):
        from starlette.responses import Response

        for debug in (True, False):
            with patch("app.core.auth.DEBUG", debug):
                r = Response()
                definir_cookie_sessao(r, "sintetico")
                self.assertEqual("; Secure" in r.headers["set-cookie"], not debug)
                self.assertIn("HttpOnly", r.headers["set-cookie"])
                remover_cookie_sessao(r)
                self.assertIn("Max-Age=0", r.headers.getlist("set-cookie")[-1])


class FluxoNavegadorTest(unittest.TestCase):
    def test_login_sessao_logout_com_origem_legitima_e_cookie_secure(self):
        e = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(e)
        with Session(e) as db:
            db.add(
                Usuario(
                    nome="Sintético",
                    email="sintetico@aluno.unb.br",
                    password_hash=gerar_hash_senha("senha sintetica segura"),
                    email_confirmado=True,
                )
            )
            db.commit()

        def banco():
            with Session(e) as db:
                yield db

        anterior = dict(app.dependency_overrides)
        app.dependency_overrides[get_db] = banco
        try:
            with TestClient(
                app, base_url="https://api.example", headers={"Origin": "http://localhost:3000"}
            ) as client:
                r = client.post(
                    "/api/auth/login",
                    json={"email": "sintetico@aluno.unb.br", "senha": "senha sintetica segura"},
                )
                self.assertEqual(r.status_code, 200)
                self.assertIn("HttpOnly", r.headers["set-cookie"])
                self.assertEqual(r.headers["cache-control"], "no-store")
                self.assertTrue(client.get("/api/auth/sessao").json()["autenticado"])
                self.assertEqual(client.post("/api/auth/logout").status_code, 200)
                self.assertFalse(client.get("/api/auth/sessao").json()["autenticado"])
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(anterior)
            e.dispose()
