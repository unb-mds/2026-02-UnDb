"""RF24: fluxo aprovado na conversa de 15/11/2026."""

import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")
os.environ.setdefault("EMAIL_BACKEND", "console")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.core.database import Base
from app.core.security import gerar_hash_senha, gerar_hash_token, verificar_senha
from app.main import app
from app.models.sessao_usuario import SessaoUsuario
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.models.usuario import Usuario
from app.routers import auth as router
from app.schemas.auth import (
    CadastroRequest,
    LoginRequest,
    RecuperarSenhaRequest,
    RedefinirSenhaRequest,
)
from app.services import auth_service as service
from app.services.email_service import ConsoleEmailSender, EmailDeliveryError, ResendEmailSender


class Sender:
    def __init__(self, falhar=False):
        self.envios = []
        self.falhar = falhar

    def enviar_recuperacao_senha(self, destinatario, link):
        if self.falhar:
            raise EmailDeliveryError("falha simulada")
        self.envios.append((destinatario, link))

    def enviar_confirmacao(self, destinatario, link):
        self.envios.append((destinatario, link))


class RecuperacaoSenhaTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.usuario = Usuario(
            nome="Maria",
            email="maria@aluno.unb.br",
            password_hash=gerar_hash_senha("senha anterior"),
            email_confirmado=False,
        )
        self.db.add(self.usuario)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def solicitar(self):
        sender = Sender()
        service.solicitar_recuperacao_senha(self.db, self.usuario.email, sender)
        link = sender.envios[0][1]
        return parse_qs(urlsplit(link).query)["token"][0]

    def test_solicitacao_generica_e_normalizacao_sem_criar_conta(self):
        sender = Sender()
        dados = RecuperarSenhaRequest(email=" MARIA@ALUNO.UNB.BR ")
        conhecida = router.recuperar_senha(dados, self.db, sender)
        desconhecida = router.recuperar_senha(
            RecuperarSenhaRequest(email="outra@aluno.unb.br"), self.db, sender
        )
        self.assertEqual(conhecida, desconhecida)
        self.assertEqual(len(sender.envios), 1)
        self.assertEqual(len(self.db.scalars(select(Usuario)).all()), 1)
        self.assertFalse(self.usuario.email_confirmado)

    def test_token_armazenado_com_hash_prazo_e_senha_preservada(self):
        token = self.solicitar()
        registro = self.db.scalar(select(TokenRecuperacaoSenha))
        self.assertEqual(registro.token_hash, gerar_hash_token(token))
        self.assertNotEqual(registro.token_hash, token)
        self.assertGreater(
            service._como_utc(registro.expires_at),
            datetime.now(timezone.utc) + timedelta(minutes=59),
        )
        self.assertLessEqual(
            service._como_utc(registro.expires_at), datetime.now(timezone.utc) + timedelta(hours=1)
        )
        self.assertTrue(verificar_senha("senha anterior", self.usuario.password_hash))

    def test_troca_invalida_sessoes_todos_links_e_senha_anterior(self):
        token = self.solicitar()
        outro = self.solicitar()
        for _ in range(2):
            service.autenticar(
                self.db, LoginRequest(email=self.usuario.email, senha="senha anterior")
            )
        resposta = Response()
        resultado = router.redefinir_senha(
            RedefinirSenhaRequest(token=token, senha="nova senha segura"), resposta, self.db
        )
        self.assertEqual(resultado.message, service.REDEFINICAO_MESSAGE)
        self.assertIn("Max-Age=0", resposta.headers["set-cookie"])
        self.assertEqual(self.db.scalars(select(SessaoUsuario)).all(), [])
        self.assertFalse(self.usuario.email_confirmado)
        for link in (token, outro):
            with self.assertRaises(service.TokenRecuperacaoInvalidoError):
                service.redefinir_senha(self.db, link, "senha adulterada")
        with self.assertRaises(service.CredenciaisInvalidasError):
            service.autenticar(
                self.db, LoginRequest(email=self.usuario.email, senha="senha anterior")
            )
        service.autenticar(
            self.db, LoginRequest(email=self.usuario.email, senha="nova senha segura")
        )

    def test_rejeita_expirado_adulterado_e_sem_mutacao(self):
        token = self.solicitar()
        registro = self.db.scalar(select(TokenRecuperacaoSenha))
        registro.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.db.commit()
        original = self.usuario.password_hash
        for link in (token, "x" * 43):
            with self.assertRaises(HTTPException) as erro:
                router.redefinir_senha(
                    RedefinirSenhaRequest(token=link, senha="nova senha segura"),
                    Response(),
                    self.db,
                )
            self.assertEqual(erro.exception.status_code, 400)
        self.assertEqual(self.usuario.password_hash, original)
        self.assertIsNone(registro.used_at)

    def test_tokens_de_confirmacao_e_recuperacao_nao_se_confundem(self):
        sender = Sender()
        service.cadastrar(
            self.db,
            CadastroRequest(
                ciencia_termos=True,
                termos_versao="2026-11-17",
                nome="Outra",
                email="outra@aluno.unb.br",
                senha="senha de cadastro",
            ),
            sender,
        )
        confirmacao = parse_qs(urlsplit(sender.envios[0][1]).query)["token"][0]
        with self.assertRaises(service.TokenRecuperacaoInvalidoError):
            service.redefinir_senha(self.db, confirmacao, "nova senha segura")
        with self.assertRaises(service.TokenConfirmacaoInvalidoError):
            service.confirmar_email(self.db, self.solicitar())

    def test_falha_envio_nao_revela_conta_nem_invalida_link_anterior(self):
        token = self.solicitar()
        with self.assertLogs("app.routers.auth", level="ERROR"):
            resposta = router.recuperar_senha(
                RecuperarSenhaRequest(email=self.usuario.email), self.db, Sender(falhar=True)
            )
        self.assertEqual(resposta.message, service.RECUPERACAO_MESSAGE)
        self.assertEqual(len(self.db.scalars(select(TokenRecuperacaoSenha)).all()), 1)
        service.redefinir_senha(self.db, token, "nova senha segura")

    def test_falha_na_troca_desfaz_hash_links_e_sessoes(self):
        token = self.solicitar()
        service.autenticar(self.db, LoginRequest(email=self.usuario.email, senha="senha anterior"))
        with patch.object(
            service.recuperacao_senha_repository,
            "invalidar_links_e_sessoes",
            side_effect=RuntimeError("falha"),
        ):
            with self.assertRaises(RuntimeError):
                service.redefinir_senha(self.db, token, "nova senha segura")
        self.assertTrue(verificar_senha("senha anterior", self.usuario.password_hash))
        self.assertIsNone(self.db.scalar(select(TokenRecuperacaoSenha)).used_at)
        self.assertEqual(len(self.db.scalars(select(SessaoUsuario)).all()), 1)

    def test_validacao_schema_e_contrato_http(self):
        for senha in ("curta", "x" * 129):
            with self.assertRaises(ValidationError):
                RedefinirSenhaRequest(token="x" * 43, senha=senha)
        with self.assertRaises(ValidationError):
            RecuperarSenhaRequest(email="outro@gmail.com")
        with self.assertRaises(ValidationError):
            RedefinirSenhaRequest(
                token="x" * 43, senha="senha de teste", email="maria@aluno.unb.br"
            )
        caminhos = app.openapi()["paths"]
        self.assertIn("202", caminhos["/api/auth/recuperar-senha"]["post"]["responses"])
        self.assertIn("200", caminhos["/api/auth/redefinir-senha"]["post"]["responses"])

    def test_adaptadores_enviam_link_com_finalidade_correta(self):
        with (
            patch("app.services.email_service.config.DEBUG", True),
            self.assertLogs("app.services.email_service", level="WARNING") as logs,
        ):
            ConsoleEmailSender().enviar_recuperacao_senha(
                "teste@aluno.unb.br", "http://localhost/redefinir-senha?token=teste"
            )
        self.assertIn("recuperacao de senha", logs.output[0])
        with patch("app.services.email_service.resend.Emails.send") as enviar:
            ResendEmailSender("chave-de-teste", "teste@example.com").enviar_recuperacao_senha(
                "teste@aluno.unb.br", "https://example.com/redefinir-senha?token=teste"
            )
            conteudo = enviar.call_args.args[0]
            self.assertIn("Redefina", conteudo["subject"])
            self.assertIn("uma hora", conteudo["html"])
        with patch(
            "app.services.email_service.resend.Emails.send", side_effect=RuntimeError("falha")
        ):
            with self.assertRaises(EmailDeliveryError):
                ResendEmailSender("teste", "teste@example.com").enviar_recuperacao_senha(
                    "teste@aluno.unb.br", "https://example.com"
                )
