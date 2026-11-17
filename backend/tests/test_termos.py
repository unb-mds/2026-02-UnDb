"""RF26: ciência explícita, persistência e compatibilidade com contas antigas."""

import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")
os.environ.setdefault("EMAIL_BACKEND", "console")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import gerar_hash_senha
from app.domain.termos import TERMOS_VERSAO
from app.main import app
from app.models.usuario import Usuario
from app.services.email_service import get_email_sender


class EmailSintetico:
    def __init__(self):
        self.envios = []

    def enviar_confirmacao(self, email, link):
        self.envios.append((email, link))


class TermosTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.email = EmailSintetico()
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_email_sender] = lambda: self.email
        self.client = TestClient(app, base_url="https://testserver")
        self.dados = dict(
            nome="Pessoa sintética",
            email="termos@aluno.unb.br",
            senha="Senha-sintetica-269!",
            ciencia_termos=True,
            termos_versao=TERMOS_VERSAO,
        )

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_rejeita_omissao_falso_coercao_versao_e_data_sem_efeitos(self):
        casos = []
        for campo in ("ciencia_termos", "termos_versao"):
            dados = dict(self.dados)
            del dados[campo]
            casos.append(dados)
        for valor in (False, None, 1, "true", "false"):
            casos.append({**self.dados, "ciencia_termos": valor})
        for valor in ("", "2020-01-01", None, 20261117):
            casos.append({**self.dados, "termos_versao": valor})
        casos.append({**self.dados, "termos_ciencia_em": "2000-01-01T00:00:00Z"})
        for dados in casos:
            with self.subTest(dados=dados):
                self.assertEqual(
                    self.client.post("/api/auth/cadastro", json=dados).status_code, 422
                )
        self.assertIsNone(self.db.scalar(select(Usuario)))
        self.assertEqual(self.email.envios, [])

    def test_cadastro_grava_versao_e_instante_servidor_sem_expor_na_resposta(self):
        agora = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
        with patch("app.services.auth_service._agora_utc", return_value=agora):
            resposta = self.client.post("/api/auth/cadastro", json=self.dados)
        self.assertEqual(resposta.status_code, 202)
        self.assertEqual(set(resposta.json()), {"message"})
        usuario = self.db.scalar(select(Usuario))
        self.assertEqual(usuario.termos_versao, TERMOS_VERSAO)
        self.assertEqual(usuario.termos_ciencia_em.replace(tzinfo=timezone.utc), agora)
        self.assertEqual(len(self.email.envios), 1)

    def test_conta_antiga_entra_e_repeticao_nao_inventa_ciencia(self):
        usuario = Usuario(
            nome="Conta antiga",
            email=self.dados["email"],
            password_hash=gerar_hash_senha(self.dados["senha"]),
            email_confirmado=True,
        )
        self.db.add(usuario)
        self.db.commit()
        resposta = self.client.post(
            "/api/auth/login",
            json={"email": self.dados["email"], "senha": self.dados["senha"]},
            headers={"Origin": "http://localhost:3000"},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(self.client.get("/api/auth/sessao").json()["autenticado"])
        self.client.cookies.clear()
        self.assertEqual(self.client.post("/api/auth/cadastro", json=self.dados).status_code, 202)
        self.db.refresh(usuario)
        self.assertIsNone(usuario.termos_versao)
        self.assertIsNone(usuario.termos_ciencia_em)
        self.assertEqual(self.email.envios, [])

    def test_banco_rejeita_ciencia_incompleta(self):
        for versao, data in (
            (TERMOS_VERSAO, None),
            (None, datetime.now(timezone.utc)),
            ("", datetime.now(timezone.utc)),
        ):
            with self.subTest(versao=versao, data=data):
                self.db.add(
                    Usuario(
                        nome="Incompleta",
                        email="incompleta@aluno.unb.br",
                        password_hash="hash-sintetico",
                        termos_versao=versao,
                        termos_ciencia_em=data,
                    )
                )
                with self.assertRaises(IntegrityError):
                    self.db.commit()
                self.db.rollback()


if __name__ == "__main__":
    unittest.main()
