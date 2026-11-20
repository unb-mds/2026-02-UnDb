"""Consulta privada autorizada na revisão final: autoria, retenção e paginação."""

import asyncio
import os
import secrets
import unittest
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.auth import SESSION_COOKIE_NAME
from app.core.database import Base, get_db
from app.core.security import gerar_hash_token
from app.main import app
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.usuario import Usuario


class MinhasAvaliacoesTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(self.engine)
        self.overrides = dict(app.dependency_overrides)

        def banco():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = banco
        self.token = secrets.token_urlsafe(32)
        self.outro_token = secrets.token_urlsafe(32)
        with Session(self.engine) as db:
            pessoa = Usuario(nome="Pessoa", email="pessoa@aluno.unb.br", password_hash="teste")
            outra = Usuario(nome="Outra", email="outra@aluno.unb.br", password_hash="teste")
            docente = Professor(nome="Docente", departamento="CIC")
            db.add_all([pessoa, outra, docente])
            db.flush()
            self.usuario_id = pessoa.id
            self.outro_id = outra.id
            for usuario, token in [(pessoa, self.token), (outra, self.outro_token)]:
                db.add(
                    SessaoUsuario(
                        usuario_id=usuario.id,
                        token_hash=gerar_hash_token(token),
                        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                    )
                )
            for i in range(13):
                disciplina = Disciplina(
                    codigo=f"CIC{i:04}", nome=f"Disciplina {i}", departamento="CIC"
                )
                db.add(disciplina)
                db.flush()
                db.add(
                    Avaliacao(
                        usuario_id=pessoa.id,
                        professor_id=docente.id,
                        disciplina_id=disciplina.id,
                        didatica=4,
                        dificuldade=Dificuldade.MEDIO,
                        chamada=False,
                        disponibiliza_material=False,
                        recomenda=True,
                        excluido_em=datetime.now(timezone.utc) if i == 12 else None,
                        updated_at=datetime(2026, 11, i + 1, tzinfo=timezone.utc),
                    )
                )
            db.commit()

    def tearDown(self):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.overrides)
        self.engine.dispose()

    def get(self, token=None, query=""):
        async def solicitar():
            headers = {"cookie": f"{SESSION_COOKIE_NAME}={token}"} if token else {}
            async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
                return await client.get("/api/avaliacoes/minhas" + query, headers=headers)

        return asyncio.run(solicitar())

    def test_exige_autenticacao_e_nao_cacheia(self):
        for token in (None, secrets.token_urlsafe(32)):
            resposta = self.get(token)
            self.assertEqual(resposta.status_code, 401)
            self.assertEqual(resposta.headers["cache-control"], "no-store")

    def test_pagina_somente_as_proprias_sem_dados_do_autor(self):
        resposta = self.get(self.token)
        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()
        self.assertEqual((dados["total"], dados["pagina"], dados["tamanho"]), (12, 1, 10))
        self.assertEqual(len(dados["itens"]), 10)
        self.assertEqual(dados["itens"][0]["disciplina"]["codigo"], "CIC0011")
        item = dados["itens"][0]
        self.assertEqual(item["didatica"], 4)
        self.assertEqual(item["professor"]["nome"], "Docente")
        self.assertNotIn("usuario_id", item)
        self.assertNotIn("email", resposta.text)
        self.assertNotIn("comentarios", item)
        self.assertEqual(resposta.headers["cache-control"], "no-store")
        self.assertEqual(resposta.headers["referrer-policy"], "no-referrer")
        segunda = self.get(self.token, "?pagina=2").json()
        self.assertEqual(len(segunda["itens"]), 2)
        self.assertTrue(
            {a["id"] for a in dados["itens"]}.isdisjoint(a["id"] for a in segunda["itens"])
        )

    def test_outra_conta_nao_consegue_ler_avaliacoes_alheias(self):
        resposta = self.get(self.outro_token, f"?usuario_id={self.usuario_id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["itens"], [])
        self.assertEqual(resposta.json()["total"], 0)
        with Session(self.engine) as db:
            db.scalar(
                select(SessaoUsuario).where(SessaoUsuario.usuario_id == self.usuario_id)
            ).expires_at = datetime.now(timezone.utc) - timedelta(days=1)
            db.commit()
        self.assertEqual(self.get(self.token).status_code, 401)

    def test_valida_pagina_e_trata_pagina_vazia(self):
        for query in ("?pagina=0", "?pagina=-1", "?pagina=x", "?pagina=100001"):
            self.assertEqual(self.get(self.token, query).status_code, 422)
        resposta = self.get(self.token, "?pagina=3").json()
        self.assertEqual(resposta["total"], 12)
        self.assertEqual(resposta["itens"], [])
