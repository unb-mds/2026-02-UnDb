"""Infraestrutura HTTP sintética; nenhum transporte externo ou segredo fixo."""

import secrets
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import config
from app.core.database import get_db
from app.core.dependencia_limite_abuso import obter_limitador
from app.core.security import gerar_hash_senha
from app.main import app
from app.models.usuario import Usuario
from app.services.email_service import EmailDeliveryError, get_email_sender


class TransporteEmMemoria:
    def __init__(self):
        self.envios = []
        self.falhar = False

    def enviar_confirmacao(self, destinatario, link):
        if self.falhar:
            raise EmailDeliveryError("falha sintética do transporte")
        self.envios.append((destinatario, link))

    enviar_recuperacao_senha = enviar_confirmacao

    def token(self, indice=-1):
        return parse_qs(urlsplit(self.envios[indice][1]).query)["token"][0]


class AuthHttpFixture:
    def iniciar_http(self, engine, limitador):
        self.engine = engine
        self.senha = secrets.token_urlsafe(24)
        self.email = f"ensaio.{uuid4().hex}@aluno.unb.br"
        self.sender = TransporteEmMemoria()
        self.overrides = dict(app.dependency_overrides)

        def banco():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = banco
        app.dependency_overrides[get_email_sender] = lambda: self.sender
        app.dependency_overrides[obter_limitador] = lambda: limitador
        self.client = TestClient(
            app, base_url="https://api.example", headers={"Origin": config.CORS_ORIGINS[0]}
        )

    def encerrar_http(self):
        self.client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.overrides)

    def post(self, rota, corpo):
        if rota == "cadastro":
            from app.domain.termos import TERMOS_VERSAO

            corpo = {"ciencia_termos": True, "termos_versao": TERMOS_VERSAO, **corpo}
        return self.client.post("/api/auth/" + rota, json=corpo)

    def usuario(self, *, email=None, confirmado=False, moderador=False):
        with Session(self.engine) as db:
            usuario = Usuario(
                nome="Pessoa sintética",
                email=email or self.email,
                password_hash=gerar_hash_senha(self.senha),
                email_confirmado=confirmado,
                moderador=moderador,
            )
            db.add(usuario)
            db.commit()
            return usuario.id

    def contar(self, modelo):
        with Session(self.engine) as db:
            return db.scalar(select(func.count()).select_from(modelo))
