import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")
from app.core.registros_acesso import RegistrosAcesso, expira_em, operacao


class AcessoTest(unittest.IsolatedAsyncioTestCase):
    def test_meses_corridos(self):
        self.assertEqual(
            expira_em(datetime(2026, 8, 31, tzinfo=timezone.utc), 6),
            datetime(2027, 2, 28, tzinfo=timezone.utc),
        )
        self.assertEqual(expira_em(datetime(2023, 8, 31, tzinfo=timezone.utc), 6).day, 29)
        with self.assertRaises(ValueError):
            expira_em(datetime.now(timezone.utc), 0)

    def test_eventos_sem_leituras_publicas(self):
        for rota in [
            "cadastro",
            "login",
            "confirmar",
            "reenviar-confirmacao",
            "recuperar-senha",
            "redefinir-senha",
            "logout",
            "conta",
        ]:
            self.assertIsNotNone(operacao("POST", "/api/auth/" + rota))
        for rota in ["/api/professores", "/api/comentarios/meu", "/health"]:
            self.assertIsNone(operacao("GET", rota))

    async def test_registro_minimo_sem_corpo_query_ou_cabecalho_de_autenticacao(self):
        id = uuid4()

        async def app(scope, receive, send):
            scope["acesso_usuario_id"] = id
            await send({"type": "http.response.start", "status": 429, "headers": []})
            await send({"type": "http.response.body", "body": b"conteudo-nao-registrado"})

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/auth/login",
            "client": ("192.0.2.1", 1),
            "query_string": b"nao-registrar",
            "headers": [(b"x-forwarded-for", b"192.0.2.2"), (b"authorization", b"nao-registrar")],
        }

        async def send(msg):
            pass

        with patch("app.core.registros_acesso.gravar") as gravar:
            await RegistrosAcesso(app)(scope, None, send)
        dados = gravar.call_args.args[0]
        self.assertEqual(dados["usuario_id"], id)
        self.assertEqual(dados["resultado"], "falha")
        self.assertEqual(dados["ip_conexao"], "192.0.2.1")
        self.assertEqual(dados["encaminhado_nao_confiavel"], "192.0.2.2")
        self.assertNotIn("nao-registrar", str(dados))
        self.assertNotIn("conteudo-nao-registrado", str(dados))

    def test_persistencia_e_purga(self):
        from sqlalchemy import create_engine, select
        from sqlalchemy.orm import Session
        from app.core.database import Base
        from app.models.registro_acesso import RegistroAcesso
        from app.repositories.registro_acesso_repository import gravar, purgar

        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        agora = datetime.now(timezone.utc)
        with Session(engine) as db:
            gravar(
                db,
                dict(
                    ocorrido_em=agora,
                    expira_em=agora,
                    operacao="auth.login",
                    resultado="falha",
                    requisicao_id=uuid4(),
                ),
            )
            self.assertEqual(purgar(db, agora, 100), 1)
            db.commit()
            self.assertIsNone(db.scalar(select(RegistroAcesso)))
        engine.dispose()
