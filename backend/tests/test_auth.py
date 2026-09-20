import os
import unittest
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")
os.environ.setdefault("EMAIL_BACKEND", "console")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")

from app.core.database import Base
from app.core.security import password_hash
from app.main import app
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.usuario import Usuario
from app.schemas.auth import CadastroRequest
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


if __name__ == "__main__":
    unittest.main()
