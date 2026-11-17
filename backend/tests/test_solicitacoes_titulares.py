"""RF25: contrato e permissões aprovados por Nicolas em 15/11/2026."""

import os
import unittest
import runpy
from pathlib import Path
from unittest.mock import patch
from uuid import UUID, uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.auth import obter_usuario_confirmado
from app.core.database import Base, get_db
from app.core.dependencia_limite_abuso import obter_limitador
from tests.auth_abuso_fixtures import protecao_permitida
from app.main import app
from app.models.solicitacao_titular import SolicitacaoTitular, EventoSolicitacao
from app.models.usuario import Usuario
from app.services import solicitacao_titular_service as service


class CanalTest(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[obter_limitador] = lambda: protecao_permitida().limitador
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.atendente = Usuario(
            id=uuid4(),
            nome="Atendente",
            email="a@aluno.unb.br",
            password_hash="teste",
            email_confirmado=True,
        )
        self.leitor = Usuario(
            id=uuid4(),
            nome="Leitor",
            email="l@aluno.unb.br",
            password_hash="teste",
            email_confirmado=True,
        )
        self.db.add_all([self.atendente, self.leitor])
        self.db.commit()
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.flags = patch.multiple(
            service.config,
            CANAL_TITULARES_ATIVO=True,
            CANAL_TITULARES_RETENCAO_APROVADA=True,
            CANAL_TITULARES_ATENDENTES=[str(self.atendente.id)],
            CANAL_TITULARES_LEITORES=[str(self.leitor.id)],
        )
        self.flags.start()

    def tearDown(self):
        self.flags.stop()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def criar(self):
        r = self.client.post(
            "/api/solicitacoes",
            json={
                "categoria": "NOTA_SUSPEITA",
                "alvo": "professor-ficticio",
                "descricao": "Solicitação sintética para teste.",
                "evidencia": "Contexto fictício",
            },
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.headers["cache-control"], "no-store")
        return r.json()

    def test_publico_confirmacao_chave_hash_e_consulta_sem_login(self):
        recibo = self.criar()
        item = self.db.get(SolicitacaoTitular, UUID(recibo["protocolo"]))
        self.assertNotEqual(item.chave_hash, recibo["chave"])
        credenciais = {k: recibo[k] for k in ("protocolo", "chave")}
        self.assertEqual(
            self.client.post("/api/solicitacoes/consultar", json=credenciais).status_code, 200
        )
        credenciais["chave"] = "x" * 43
        self.assertEqual(
            self.client.post("/api/solicitacoes/consultar", json=credenciais).status_code, 404
        )

    def test_permissoes_e_separacao_do_historico(self):
        r = self.criar()
        path = f"/api/atendimento/{r['protocolo']}/eventos"
        app.dependency_overrides[obter_usuario_confirmado] = lambda: self.leitor
        self.assertEqual(self.client.get("/api/atendimento").status_code, 200)
        self.assertEqual(
            self.client.post(
                path, json={"tipo": "RESPOSTA", "texto": "não autorizado"}
            ).status_code,
            403,
        )
        app.dependency_overrides[obter_usuario_confirmado] = lambda: self.atendente
        for tipo in ("TRIAGEM", "PROVIDENCIA", "RESPOSTA"):
            self.assertEqual(
                self.client.post(path, json={"tipo": tipo, "texto": tipo}).status_code, 200
            )
        consulta = self.client.post(
            "/api/solicitacoes/consultar", json={k: r[k] for k in ("protocolo", "chave")}
        ).json()
        self.assertEqual([e["tipo"] for e in consulta["historico"]], ["RESPOSTA"])
        self.assertNotIn("responsavel_id", consulta["historico"][0])

    def test_conta_fora_da_lista_e_ativacao_bloqueada(self):
        usuario = Usuario(id=uuid4(), nome="Outro", email="o@aluno.unb.br", password_hash="teste")
        with self.assertRaises(HTTPException):
            service.autorizar(usuario)
        with patch.object(service.config, "CANAL_TITULARES_RETENCAO_APROVADA", False):
            self.assertFalse(self.client.get("/api/solicitacoes/disponibilidade").json()["ativo"])
            self.assertEqual(
                self.client.post(
                    "/api/solicitacoes",
                    json={
                        "categoria": "OUTRA",
                        "alvo": "teste",
                        "descricao": "Descrição sintética.",
                        "evidencia": "teste",
                    },
                ).status_code,
                503,
            )

    def test_validacao_e_complemento_para_revisao(self):
        self.assertEqual(
            self.client.post("/api/solicitacoes", json={"categoria": "inventada"}).status_code, 422
        )
        r = self.criar()
        dados = {k: r[k] for k in ("protocolo", "chave")}
        r2 = self.client.post(
            "/api/solicitacoes/complementos",
            json={**dados, "texto": "Peço revisão da decisão pelo contexto fictício."},
        )
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["historico"][0]["tipo"], "COMPLEMENTO")

    def test_sem_sessao_sem_acesso_e_erros_nao_armazenaveis(self):
        self.assertEqual(self.client.get("/api/atendimento").status_code, 401)
        recibo = self.criar()
        credenciais = {k: recibo[k] for k in ("protocolo", "chave")}
        outro = self.criar()
        credenciais["protocolo"] = outro["protocolo"]
        r = self.client.post("/api/solicitacoes/consultar", json=credenciais)
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.headers["cache-control"], "no-store")

    def test_migracao_cria_tabelas_e_indice_somente_em_banco_sintetico(self):
        self.db.close()
        EventoSolicitacao.__table__.drop(self.engine)
        SolicitacaoTitular.__table__.drop(self.engine)
        migration = runpy.run_path(
            str(
                Path(__file__).resolve().parents[1]
                / "alembic/versions/20261115_02_canal_titulares.py"
            )
        )
        with self.engine.begin() as conn:
            with Operations.context(MigrationContext.configure(conn)):
                migration["upgrade"]()
            schema = inspect(conn)
            self.assertIn(
                "chave_hash", [c["name"] for c in schema.get_columns("solicitacoes_titulares")]
            )
            self.assertEqual(len(schema.get_foreign_keys("eventos_solicitacoes")), 2)
            self.assertIn(
                "ix_eventos_solicitacoes_solicitacao_id",
                [i["name"] for i in schema.get_indexes("eventos_solicitacoes")],
            )
