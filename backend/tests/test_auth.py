import os
import unittest
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")
os.environ.setdefault("EMAIL_BACKEND", "console")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")

from app.core.auth import (
    SESSION_COOKIE_NAME,
    definir_cookie_sessao,
    obter_sessao_autenticada,
    obter_sessao_opcional,
    obter_usuario_confirmado,
)
from app.core.config import DEBUG
from app.core.database import Base
from app.core.security import gerar_hash_senha, gerar_hash_token, password_hash
from app.main import app
from app.models.sessao_usuario import SessaoUsuario
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.usuario import Usuario
from app.routers import auth as auth_router
from app.schemas.auth import CadastroRequest, LoginRequest
from app.services import auth_service
from app.services.email_service import EmailDeliveryError


class FakeEmailSender:
    def __init__(self, falhar: bool = False) -> None:
        self.falhar = falhar
        self.envios: list[tuple[str, str]] = []

    def enviar_confirmacao(self, destinatario: str, link: str) -> None:
        if self.falhar:
            raise EmailDeliveryError("falha simulada")
        self.envios.append((destinatario, link))


class AuthSchemaTest(unittest.TestCase):
    def test_normaliza_nome_e_email_institucional(self) -> None:
        dados = CadastroRequest(
            nome="  Maria da Silva  ",
            email="  MARIA@ALUNO.UNB.BR ",
            senha="uma senha longa e segura",
        )
        self.assertEqual(dados.nome, "Maria da Silva")
        self.assertEqual(dados.email, "maria@aluno.unb.br")

    def test_rejeita_dominio_externo_subdominio_e_campos_extras(self) -> None:
        casos = ["maria@gmail.com", "maria@sub.aluno.unb.br"]
        for email in casos:
            with self.subTest(email=email), self.assertRaises(ValidationError):
                CadastroRequest(
                    nome="Maria",
                    email=email,
                    senha="uma senha longa e segura",
                )

        with self.assertRaises(ValidationError):
            CadastroRequest.model_validate(
                {
                    "nome": "Maria",
                    "email": "maria@aluno.unb.br",
                    "senha": "uma senha longa e segura",
                    "matricula": "000000000",
                }
            )

    def test_rejeita_senha_fora_do_intervalo_aprovado(self) -> None:
        CadastroRequest(
            nome="Maria",
            email="maria@aluno.unb.br",
            senha="12345678",
        )

        for senha in ("1234567", "x" * 129):
            with self.subTest(tamanho=len(senha)), self.assertRaises(ValidationError):
                CadastroRequest(
                    nome="Maria",
                    email="maria@aluno.unb.br",
                    senha=senha,
                )

    def test_normaliza_email_no_login(self) -> None:
        dados = LoginRequest(email="  MARIA@ALUNO.UNB.BR ", senha="senha válida")
        self.assertEqual(dados.email, "maria@aluno.unb.br")


class AuthServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.dados = CadastroRequest(
            nome="Maria",
            email="maria@aluno.unb.br",
            senha="uma senha longa e segura",
        )

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_cadastra_nao_confirmado_com_hash_e_link(self) -> None:
        sender = FakeEmailSender()
        mensagem = auth_service.cadastrar(self.db, self.dados, sender)

        usuario = self.db.scalar(select(Usuario))
        token = self.db.scalar(select(TokenConfirmacaoEmail))
        self.assertEqual(mensagem, auth_service.CADASTRO_MESSAGE)
        self.assertIsNotNone(usuario)
        self.assertFalse(usuario.email_confirmado)
        self.assertNotEqual(usuario.password_hash, self.dados.senha)
        self.assertTrue(password_hash.verify(self.dados.senha, usuario.password_hash))
        self.assertEqual(len(sender.envios), 1)
        self.assertIn("/confirmar-email?token=", sender.envios[0][1])
        token_aberto = sender.envios[0][1].split("token=", 1)[1]
        self.assertNotEqual(token.token_hash, token_aberto)

    def test_email_duplicado_tem_resposta_generica_sem_mutacao(self) -> None:
        primeiro_sender = FakeEmailSender()
        auth_service.cadastrar(self.db, self.dados, primeiro_sender)
        usuario_original = self.db.scalar(select(Usuario))
        hash_original = usuario_original.password_hash

        segundo_sender = FakeEmailSender()
        duplicado = CadastroRequest(
            nome="Outro nome",
            email="MARIA@ALUNO.UNB.BR",
            senha="outra senha longa e segura",
        )
        mensagem = auth_service.cadastrar(self.db, duplicado, segundo_sender)

        self.db.expire_all()
        usuario = self.db.scalar(select(Usuario))
        quantidade = self.db.scalar(select(func.count()).select_from(Usuario))
        self.assertEqual(mensagem, auth_service.CADASTRO_MESSAGE)
        self.assertEqual(quantidade, 1)
        self.assertEqual(usuario.nome, "Maria")
        self.assertEqual(usuario.password_hash, hash_original)
        self.assertEqual(segundo_sender.envios, [])

    def test_confirma_token_valido_e_reuso_e_idempotente(self) -> None:
        sender = FakeEmailSender()
        auth_service.cadastrar(self.db, self.dados, sender)
        token_aberto = sender.envios[0][1].split("token=", 1)[1]

        primeira = auth_service.confirmar_email(self.db, token_aberto)
        segunda = auth_service.confirmar_email(self.db, token_aberto)

        usuario = self.db.scalar(select(Usuario))
        token = self.db.scalar(select(TokenConfirmacaoEmail))
        self.assertEqual(primeira, auth_service.CONFIRMACAO_MESSAGE)
        self.assertEqual(segunda, auth_service.CONFIRMACAO_MESSAGE)
        self.assertTrue(usuario.email_confirmado)
        self.assertIsNotNone(token.used_at)

    def test_rejeita_token_expirado_ou_adulterado(self) -> None:
        sender = FakeEmailSender()
        auth_service.cadastrar(self.db, self.dados, sender)
        token_aberto = sender.envios[0][1].split("token=", 1)[1]
        token = self.db.scalar(select(TokenConfirmacaoEmail))
        token.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.db.commit()

        for valor in (token_aberto, "x" * 43):
            with self.subTest(valor=valor), self.assertRaises(
                auth_service.TokenConfirmacaoInvalidoError
            ):
                auth_service.confirmar_email(self.db, valor)

    def test_falha_de_envio_desfaz_cadastro(self) -> None:
        with self.assertRaises(EmailDeliveryError):
            auth_service.cadastrar(self.db, self.dados, FakeEmailSender(falhar=True))
        quantidade = self.db.scalar(select(func.count()).select_from(Usuario))
        self.assertEqual(quantidade, 0)

    def test_contrato_auth_esta_no_openapi(self) -> None:
        caminhos = app.openapi()["paths"]
        self.assertIn("/api/auth/cadastro", caminhos)
        self.assertIn("/api/auth/confirmar", caminhos)
        self.assertIn("/api/auth/login", caminhos)
        self.assertIn("/api/auth/sessao", caminhos)
        self.assertIn("/api/auth/logout", caminhos)

    def _criar_usuario(self, *, confirmado: bool = True) -> Usuario:
        usuario = Usuario(
            nome="Maria",
            email="maria@aluno.unb.br",
            password_hash=gerar_hash_senha("uma senha longa e segura"),
            email_confirmado=confirmado,
        )
        self.db.add(usuario)
        self.db.commit()
        return usuario

    def test_login_valido_cria_sessao_persistida_sem_armazenar_token_aberto(self) -> None:
        usuario = self._criar_usuario()

        autenticacao = auth_service.autenticar(
            self.db,
            LoginRequest(
                email="MARIA@ALUNO.UNB.BR",
                senha="uma senha longa e segura",
            ),
        )

        sessao = self.db.scalar(select(SessaoUsuario))
        self.assertEqual(autenticacao.usuario.id, usuario.id)
        self.assertIsNotNone(sessao)
        self.assertEqual(sessao.usuario_id, usuario.id)
        self.assertEqual(sessao.token_hash, gerar_hash_token(autenticacao.token))
        self.assertNotEqual(sessao.token_hash, autenticacao.token)
        self.assertGreater(
            auth_service._como_utc(sessao.expires_at),
            datetime.now(timezone.utc) + timedelta(days=6, hours=23),
        )

    def test_credenciais_invalidas_nao_criam_sessao(self) -> None:
        self._criar_usuario()

        for email, senha in (
            ("desconhecida@aluno.unb.br", "uma senha longa e segura"),
            ("maria@aluno.unb.br", "senha incorreta"),
        ):
            with self.subTest(email=email), self.assertRaises(
                auth_service.CredenciaisInvalidasError
            ):
                auth_service.autenticar(
                    self.db, LoginRequest(email=email, senha=senha)
                )

        quantidade = self.db.scalar(select(func.count()).select_from(SessaoUsuario))
        self.assertEqual(quantidade, 0)

    def test_endpoint_login_define_cookie_e_credencial_invalida_retorna_401(self) -> None:
        self._criar_usuario()
        response = Response()

        resultado = auth_router.login(
            LoginRequest(
                email="maria@aluno.unb.br",
                senha="uma senha longa e segura",
            ),
            response,
            self.db,
        )

        self.assertEqual(resultado.message, auth_service.LOGIN_MESSAGE)
        self.assertIn(SESSION_COOKIE_NAME, response.headers["set-cookie"])

        with self.assertRaises(HTTPException) as contexto:
            auth_router.login(
                LoginRequest(
                    email="maria@aluno.unb.br",
                    senha="senha incorreta",
                ),
                Response(),
                self.db,
            )
        self.assertEqual(contexto.exception.status_code, 401)

    def test_atividade_autenticada_renova_sessao_por_sete_dias(self) -> None:
        self._criar_usuario()
        autenticacao = auth_service.autenticar(
            self.db,
            LoginRequest(
                email="maria@aluno.unb.br",
                senha="uma senha longa e segura",
            ),
        )
        sessao = self.db.scalar(select(SessaoUsuario))
        sessao.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        self.db.commit()

        renovada = auth_service.validar_e_renovar_sessao(
            self.db, autenticacao.token
        )

        self.assertGreater(
            auth_service._como_utc(renovada.expires_at),
            datetime.now(timezone.utc) + timedelta(days=6, hours=23),
        )

    def test_sessao_expirada_e_removida_e_rejeitada(self) -> None:
        self._criar_usuario()
        autenticacao = auth_service.autenticar(
            self.db,
            LoginRequest(
                email="maria@aluno.unb.br",
                senha="uma senha longa e segura",
            ),
        )
        sessao = self.db.scalar(select(SessaoUsuario))
        sessao.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.db.commit()

        with self.assertRaises(auth_service.SessaoInvalidaError):
            auth_service.validar_e_renovar_sessao(self.db, autenticacao.token)

        quantidade = self.db.scalar(select(func.count()).select_from(SessaoUsuario))
        self.assertEqual(quantidade, 0)

    def test_logout_invalida_sessao(self) -> None:
        self._criar_usuario()
        autenticacao = auth_service.autenticar(
            self.db,
            LoginRequest(
                email="maria@aluno.unb.br",
                senha="uma senha longa e segura",
            ),
        )
        sessao = auth_service.validar_e_renovar_sessao(
            self.db, autenticacao.token
        )

        mensagem = auth_service.encerrar_sessao(self.db, sessao)

        self.assertEqual(mensagem, auth_service.LOGOUT_MESSAGE)
        with self.assertRaises(auth_service.SessaoInvalidaError):
            auth_service.validar_e_renovar_sessao(self.db, autenticacao.token)

    def test_endpoint_logout_invalida_sessao_e_remove_cookie(self) -> None:
        self._criar_usuario()
        autenticacao = auth_service.autenticar(
            self.db,
            LoginRequest(
                email="maria@aluno.unb.br",
                senha="uma senha longa e segura",
            ),
        )
        sessao = auth_service.validar_e_renovar_sessao(
            self.db, autenticacao.token
        )
        response = Response()

        resultado = auth_router.logout(response, sessao, self.db)

        self.assertEqual(resultado.message, auth_service.LOGOUT_MESSAGE)
        cookie = response.headers["set-cookie"]
        self.assertIn(f"{SESSION_COOKIE_NAME}=", cookie)
        self.assertIn("Max-Age=0", cookie)
        with self.assertRaises(auth_service.SessaoInvalidaError):
            auth_service.validar_e_renovar_sessao(self.db, autenticacao.token)

    def test_cookie_de_sessao_tem_atributos_aprovados(self) -> None:
        response = Response()

        definir_cookie_sessao(response, "token-aleatorio")

        cookie = response.headers["set-cookie"]
        self.assertIn(f"{SESSION_COOKIE_NAME}=token-aleatorio", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=lax", cookie)
        self.assertIn("Path=/", cookie)
        self.assertIn("Max-Age=604800", cookie)
        if DEBUG:
            self.assertNotIn("; Secure", cookie)
        else:
            self.assertIn("; Secure", cookie)

    def test_dependencia_autenticada_aceita_cookie_e_o_renova(self) -> None:
        self._criar_usuario()
        autenticacao = auth_service.autenticar(
            self.db,
            LoginRequest(
                email="maria@aluno.unb.br",
                senha="uma senha longa e segura",
            ),
        )
        request = Request(
            {
                "type": "http",
                "headers": [
                    (
                        b"cookie",
                        f"{SESSION_COOKIE_NAME}={autenticacao.token}".encode(),
                    )
                ],
            }
        )
        response = Response()

        sessao = obter_sessao_autenticada(request, response, self.db)

        self.assertEqual(sessao.usuario.email, "maria@aluno.unb.br")
        self.assertIn(SESSION_COOKIE_NAME, response.headers["set-cookie"])
        self.assertIn("Max-Age=604800", response.headers["set-cookie"])

    def test_dependencia_autenticada_rejeita_ausencia_de_cookie(self) -> None:
        request = Request({"type": "http", "headers": []})
        response = Response()

        with self.assertRaises(HTTPException) as contexto:
            obter_sessao_autenticada(request, response, self.db)

        self.assertEqual(contexto.exception.status_code, 401)
        self.assertIn(SESSION_COOKIE_NAME, response.headers["set-cookie"])

    def test_consulta_de_sessao_reflete_cookie_persistido(self) -> None:
        self._criar_usuario()
        autenticacao = auth_service.autenticar(
            self.db,
            LoginRequest(
                email="maria@aluno.unb.br",
                senha="uma senha longa e segura",
            ),
        )
        request = Request(
            {
                "type": "http",
                "headers": [
                    (
                        b"cookie",
                        f"{SESSION_COOKIE_NAME}={autenticacao.token}".encode(),
                    )
                ],
            }
        )
        response = Response()

        sessao = obter_sessao_opcional(request, response, self.db)
        resultado = auth_router.consultar_sessao(sessao)

        self.assertTrue(resultado.autenticado)
        self.assertIn("Max-Age=604800", response.headers["set-cookie"])

    def test_consulta_de_sessao_limpa_cookie_invalido(self) -> None:
        request = Request(
            {
                "type": "http",
                "headers": [(b"cookie", f"{SESSION_COOKIE_NAME}=invalido".encode())],
            }
        )
        response = Response()

        sessao = obter_sessao_opcional(request, response, self.db)
        resultado = auth_router.consultar_sessao(sessao)

        self.assertFalse(resultado.autenticado)
        self.assertIn("Max-Age=0", response.headers["set-cookie"])

    def test_usuario_sem_email_confirmado_e_bloqueado_para_escrita(self) -> None:
        usuario = self._criar_usuario(confirmado=False)

        with self.assertRaises(HTTPException) as contexto:
            obter_usuario_confirmado(usuario)

        self.assertEqual(contexto.exception.status_code, 403)

    def test_usuario_confirmado_e_disponibilizado_para_escrita(self) -> None:
        usuario = self._criar_usuario(confirmado=True)

        resultado = obter_usuario_confirmado(usuario)

        self.assertEqual(resultado.id, usuario.id)


if __name__ == "__main__":
    unittest.main()
