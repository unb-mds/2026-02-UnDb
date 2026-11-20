"""#266/bloco 2: negação antes de efeitos, neutralidade e contratos existentes."""

import os
import secrets
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", secrets.token_urlsafe(32))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core import config
from app.core.database import Base
from app.core.dependencia_limite_abuso import obter_limitador
from app.core.security import verificar_senha
from app.domain.limite_abuso import MotivoLimite, ResultadoLimite
from app.main import app
from app.models.sessao_usuario import SessaoUsuario
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest
from app.services import auth_service
from app.services.limite_abuso_service import LimitadorAbuso
from app.services.email_service import EmailDeliveryError, get_email_sender
from tests.auth_http_fixtures import AuthHttpFixture


class AuthAbusoHttpTest(AuthHttpFixture, unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(engine)
        self.limitador = Mock(spec=LimitadorAbuso)
        self.limitador.consumir.return_value = ResultadoLimite(True, 0, MotivoLimite.PERMITIDO)
        self.limitador.reiniciar_identidade.return_value = True
        self.limitador.falha.return_value = ResultadoLimite(
            False, 5, MotivoLimite.INDISPONIVEL, indisponivel=True
        )
        self.iniciar_http(engine, self.limitador)

    def tearDown(self):
        self.encerrar_http()
        self.engine.dispose()

    def test_todos_post_protegidos_negam_429_503_antes_de_efeitos(self):
        casos = [
            (
                "cadastro",
                {"nome": "Sintético", "email": self.email, "senha": self.senha},
                "cadastrar",
            ),
            ("login", {"email": self.email, "senha": self.senha}, "autenticar"),
            ("confirmar", {"token": secrets.token_urlsafe(32)}, "confirmar_email"),
            ("reenviar-confirmacao", {"email": self.email}, "reenviar_confirmacao"),
            ("recuperar-senha", {"email": self.email}, "solicitar_recuperacao_senha"),
            (
                "redefinir-senha",
                {"token": secrets.token_urlsafe(32), "senha": self.senha},
                "redefinir_senha",
            ),
        ]
        for indisponivel, status in ((False, 429), (True, 503)):
            self.limitador.consumir.return_value = ResultadoLimite(
                False, 7, MotivoLimite.GLOBAL, indisponivel=indisponivel
            )
            for rota, corpo, funcao in casos:
                with (
                    self.subTest(rota=rota, status=status),
                    patch.object(auth_service, funcao) as efeito,
                ):
                    r = self.post(rota, corpo)
                    self.assertEqual(r.status_code, status)
                    self.assertEqual(r.headers["retry-after"], "7")
                    self.assertEqual(r.headers["cache-control"], "no-store")
                    self.assertEqual(r.headers["referrer-policy"], "no-referrer")
                    self.assertNotIn("set-cookie", r.headers)
                    self.assertNotIn(self.email, r.text)
                    self.assertNotIn(self.senha, r.text)
                    efeito.assert_not_called()
        self.assertEqual(self.sender.envios, [])
        for modelo in (Usuario, SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
            self.assertEqual(self.contar(modelo), 0)

    def test_cadastro_neutro_para_conta_existente_e_nova(self):
        self.usuario()
        nova = f"outra.{uuid4().hex}@aluno.unb.br"
        respostas = [
            self.post("cadastro", {"nome": "Pessoa sintética", "email": email, "senha": self.senha})
            for email in (self.email, nova)
        ]
        self.assertEqual([r.status_code for r in respostas], [202, 202])
        self.assertEqual(respostas[0].json(), respostas[1].json())
        self.assertEqual(len(self.sender.envios), 1)
        self.assertEqual(self.contar(Usuario), 2)

    def test_recuperacao_e_reenvio_neutros_para_conta_existente_ou_inexistente(self):
        self.usuario()
        for rota in ("recuperar-senha", "reenviar-confirmacao"):
            antes = len(self.sender.envios)
            conhecida = self.post(rota, {"email": self.email})
            desconhecida = self.post(rota, {"email": f"ausente.{uuid4().hex}@aluno.unb.br"})
            self.assertEqual(conhecida.status_code, 202)
            self.assertEqual(desconhecida.status_code, 202)
            self.assertEqual(conhecida.json(), desconhecida.json())
            self.assertEqual(len(self.sender.envios), antes + 1)

    def test_falha_provedor_neutra_e_sem_tokens_ou_conta_parcial(self):
        self.sender.falhar = True
        with self.assertLogs("app.routers.auth", level="ERROR") as logs:
            r = self.post(
                "cadastro", {"nome": "Sintético", "email": self.email, "senha": self.senha}
            )
        self.assertEqual(r.status_code, 202)
        self.assertEqual(self.contar(Usuario), 0)
        self.assertEqual(self.contar(TokenConfirmacaoEmail), 0)
        self.usuario()
        for rota in ("recuperar-senha", "reenviar-confirmacao"):
            with self.assertLogs("app.routers.auth", level="ERROR"):
                self.assertEqual(self.post(rota, {"email": self.email}).status_code, 202)
        self.assertEqual(self.contar(TokenRecuperacaoSenha), 0)
        self.assertEqual(self.contar(TokenConfirmacaoEmail), 0)
        self.assertNotIn(self.email, str(logs.output))

    def test_login_desconhecido_e_senha_errada_mesmo_contrato_e_verificacao(self):
        self.usuario()
        with patch.object(
            auth_service, "verificar_senha", wraps=auth_service.verificar_senha
        ) as verificar:
            conhecida = self.post(
                "login", {"email": self.email, "senha": secrets.token_urlsafe(24)}
            )
            desconhecida = self.post(
                "login", {"email": "ausente@aluno.unb.br", "senha": self.senha}
            )
        self.assertEqual(conhecida.status_code, 401)
        self.assertEqual(desconhecida.status_code, 401)
        self.assertEqual(conhecida.json(), desconhecida.json())
        self.assertEqual(verificar.call_count, 2)
        self.assertEqual(self.contar(SessaoUsuario), 0)

    def test_falha_reset_contador_nao_emite_sessao_ou_cookie(self):
        self.usuario()
        self.limitador.reiniciar_identidade.return_value = False
        r = self.post("login", {"email": self.email, "senha": self.senha})
        self.assertEqual(r.status_code, 503)
        self.assertNotIn("set-cookie", r.headers)
        self.assertEqual(self.contar(SessaoUsuario), 0)

    def test_falha_na_configuracao_do_transporte_503_neutro_antes_de_efeitos(self):
        def indisponivel():
            raise EmailDeliveryError("marcador privado do provedor")

        app.dependency_overrides[get_email_sender] = indisponivel
        for rota, dados in (
            ("cadastro", {"nome": "Sintético", "email": self.email, "senha": self.senha}),
            ("recuperar-senha", {"email": self.email}),
            ("reenviar-confirmacao", {"email": self.email}),
        ):
            r = self.post(rota, dados)
            self.assertEqual(r.status_code, 503)
            self.assertIn("retry-after", r.headers)
            self.assertNotIn("marcador", r.text)
        self.assertEqual(self.contar(Usuario), 0)

    def test_reenvio_preserva_links_prazo_e_retorno_validado(self):
        self.post(
            "cadastro", {"nome": "Pessoa sintética", "email": self.email, "senha": self.senha}
        )
        anterior = self.sender.token()
        destino = f"/professores/{uuid4()}/disciplinas/{uuid4()}/avaliar"
        r = self.post("reenviar-confirmacao", {"email": self.email.upper(), "return_to": destino})
        self.assertEqual(r.status_code, 202)
        self.assertEqual(parse_qs(urlsplit(self.sender.envios[-1][1]).query)["returnTo"], [destino])
        self.assertNotEqual(anterior, self.sender.token())
        self.assertEqual(self.contar(TokenConfirmacaoEmail), 2)
        self.assertEqual(self.post("confirmar", {"token": anterior}).status_code, 200)
        self.assertEqual(self.post("confirmar", {"token": anterior}).status_code, 400)
        enviados = len(self.sender.envios)
        self.assertEqual(self.post("reenviar-confirmacao", {"email": self.email}).status_code, 202)
        self.assertEqual(len(self.sender.envios), enviados)
        self.assertEqual(
            self.post(
                "reenviar-confirmacao",
                {"email": self.email, "return_to": "https://externa.example"},
            ).status_code,
            422,
        )

    def test_troca_de_senha_reverte_se_reset_do_limitador_falhar(self):
        usuario_id = self.usuario()
        self.post("recuperar-senha", {"email": self.email})
        token = self.sender.token()
        with Session(self.engine) as db:
            auth_service.autenticar(db, LoginRequest(email=self.email, senha=self.senha))
        self.limitador.reiniciar_identidade.return_value = False
        nova_senha = secrets.token_urlsafe(24)
        r = self.post("redefinir-senha", {"token": token, "senha": nova_senha})
        self.assertEqual(r.status_code, 503)
        with Session(self.engine) as db:
            usuario = db.get(Usuario, usuario_id)
            self.assertTrue(verificar_senha(self.senha, usuario.password_hash))
            self.assertFalse(verificar_senha(nova_senha, usuario.password_hash))
            self.assertIsNone(db.scalar(select(TokenRecuperacaoSenha)).used_at)
        self.assertEqual(self.contar(SessaoUsuario), 1)

    def test_sessao_e_logout_nao_consultam_limitador(self):
        self.usuario()
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": self.senha}).status_code, 200
        )
        self.limitador.reset_mock()
        self.limitador.consumir.side_effect = AssertionError("não consultar o limitador")
        self.assertTrue(self.client.get("/api/auth/sessao").json()["autenticado"])
        self.assertEqual(self.post("logout", None).status_code, 200)
        self.limitador.consumir.assert_not_called()
        self.assertFalse(self.client.get("/api/auth/sessao").json()["autenticado"])

    def test_ausencia_segredo_falha_fechada_sem_banco_ou_dados_no_erro(self):
        fabrica = Mock()
        app.dependency_overrides[obter_limitador] = lambda: LimitadorAbuso(fabrica)
        with patch.object(config, "ABUSO_HMAC_SECRET", ""):
            r = self.post("login", {"email": self.email, "senha": self.senha})
        self.assertEqual(r.status_code, 503)
        self.assertNotIn(self.email, r.text)
        fabrica.assert_not_called()

    def test_openapi_documenta_reenvio_e_respostas_temporarias(self):
        paths = app.openapi()["paths"]
        for rota in (
            "cadastro",
            "login",
            "confirmar",
            "reenviar-confirmacao",
            "recuperar-senha",
            "redefinir-senha",
        ):
            respostas = paths[f"/api/auth/{rota}"]["post"]["responses"]
            self.assertIn("429", respostas)
            self.assertIn("503", respostas)
