"""Decisão B do PO: janela exata, cascatas, credenciais e autorização."""

import os
import secrets
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")
from sqlalchemy import create_engine, select, delete, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
from app.core import config
from app.core.database import Base
from app.models import (
    Usuario,
    Professor,
    Disciplina,
    Avaliacao,
    ComentarioVersao,
    Denuncia,
    DecisaoModeracao,
    Agradecimento,
    SessaoUsuario,
    TokenConfirmacaoEmail,
    TokenRecuperacaoSenha,
)
from app.models.enums import EstadoComentario, MotivoDenuncia
from app.schemas.auth import CadastroRequest, LoginRequest
from app.repositories import (
    retencao_repository as repo,
    avaliacao_repository,
    denuncia_repository,
    moderacao_repository,
)
from app.services import retencao_service as service, auth_service
from tests.auth_http_fixtures import AuthHttpFixture
from tests.auth_abuso_fixtures import protecao_permitida
from tests.test_limite_abuso_postgres import engine_ensaio


class Casos:
    def test_purga_expirados_preserva_ativos(self):
        from app.models.contador_abuso import ContadorAbuso

        for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
            for delta in (-1, 1):
                self.db.add(
                    modelo(
                        usuario_id=self.u.id,
                        token_hash=secrets.token_hex(32),
                        expires_at=self.agora + timedelta(seconds=delta),
                    )
                )
        chave = secrets.token_hex(32)
        op = "ensaio_" + uuid4().hex
        self.db.add(
            ContadorAbuso(
                operacao=op,
                chave=chave,
                quantidade=1,
                inicio_em=self.agora - timedelta(seconds=2),
                expira_em=self.agora,
            )
        )
        self.db.commit()
        service.purgar(self.db)
        for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
            self.assertEqual(
                self.db.scalar(
                    select(func.count()).select_from(modelo).where(modelo.usuario_id == self.u.id)
                ),
                1,
            )
        self.assertIsNone(self.db.get(ContadorAbuso, (op, chave)))

    def test_denuncia_encerrada_preservada_sem_impedir_nova(self):
        denuncia_repository.encerrar(self.db, self.c.id, "MANTIDO")
        denuncia_repository.criar(self.db, self.c.id, self.mod.id, MotivoDenuncia.SPAM, self.agora)
        self.db.commit()
        self.assertEqual(len(denuncia_repository.listar(self.db, self.c.id)), 1)
        self.assertEqual(
            self.db.scalar(
                select(func.count())
                .select_from(Denuncia)
                .where(Denuncia.comentario_versao_id == self.c.id)
            ),
            2,
        )

    def setUp(self):
        if hasattr(self, "pg_engine"):
            self.engine = self.pg_engine
        else:
            self.engine = create_engine(
                "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
            )
            with self.engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA foreign_keys=ON")
            Base.metadata.create_all(self.engine)
        self.iniciar_http(self.engine, protecao_permitida().limitador)
        self.db = Session(self.engine, expire_on_commit=False)
        self.agora = datetime(2026, 11, 17, 12, tzinfo=timezone.utc)
        self.clock = patch.object(service, "agora_utc", return_value=self.agora)
        self.relogio = self.clock.start()
        self.u = Usuario(
            id=uuid4(),
            nome="Sintético",
            email=self.email,
            password_hash=auth_service.gerar_hash_senha(self.senha),
            email_confirmado=True,
        )
        self.mod = Usuario(
            id=uuid4(),
            nome="Equipe",
            email=f"{uuid4().hex}@aluno.unb.br",
            password_hash="inutilizavel",
            email_confirmado=True,
            moderador=True,
        )
        self.p = Professor(id=uuid4(), nome="Ensaio", departamento="CIC")
        self.d = Disciplina(id=uuid4(), codigo=uuid4().hex[:18], nome="Ensaio", departamento="CIC")
        self.u.termos_versao = "2026-11-17"
        self.u.termos_ciencia_em = self.agora
        self.db.add_all([self.u, self.mod, self.p, self.d])
        self.db.flush()
        self.a = Avaliacao(
            id=uuid4(),
            usuario_id=self.u.id,
            professor_id=self.p.id,
            disciplina_id=self.d.id,
            didatica=3,
            dificuldade="MEDIO",
            chamada=False,
            disponibiliza_material=False,
            recomenda=True,
        )
        self.db.add(self.a)
        self.db.flush()
        self.c = ComentarioVersao(
            id=uuid4(),
            avaliacao_id=self.a.id,
            estado=EstadoComentario.PUBLICADO,
            texto="Texto sintético",
        )
        self.db.add(self.c)
        self.db.flush()
        self.db.add(
            Denuncia(
                comentario_versao_id=self.c.id,
                denunciante_id=self.mod.id,
                motivo=MotivoDenuncia.SPAM,
                created_at=self.agora,
            )
        )
        self.db.add(
            Agradecimento(
                comentario_versao_id=self.c.id,
                usuario_id=self.mod.id,
                evento="REMOCAO",
                created_at=self.agora,
            )
        )
        self.db.commit()
        self.ids = (self.u.id, self.mod.id, self.a.id, self.p.id, self.d.id)

    def tearDown(self):
        self.clock.stop()
        self.db.rollback()
        uid, mid, aid, pid, did = self.ids
        repo.apagar_comentarios(
            self.db,
            list(
                self.db.scalars(
                    select(ComentarioVersao.id).where(ComentarioVersao.avaliacao_id == aid)
                )
            ),
        )
        self.db.execute(delete(Avaliacao).where(Avaliacao.id == aid))
        for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
            self.db.execute(delete(modelo).where(modelo.usuario_id.in_([uid, mid])))
        self.db.execute(delete(Usuario).where(Usuario.id.in_([uid, mid])))
        self.db.execute(delete(Professor).where(Professor.id == pid))
        self.db.execute(delete(Disciplina).where(Disciplina.id == did))
        self.db.commit()
        self.db.close()
        self.encerrar_http()
        if not hasattr(self, "pg_engine"):
            self.engine.dispose()

    def test_janela_cascata_e_idempotencia(self):
        service.excluir_avaliacao(self.db, self.u, self.a.id)
        self.db.expire_all()
        self.assertEqual(
            avaliacao_repository.listar_por_professor_e_disciplina(self.db, self.p.id, self.d.id),
            [],
        )
        self.assertEqual(denuncia_repository.listar(self.db, self.c.id), [])
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Denuncia)), 1)
        self.relogio.return_value = (
            self.agora + timedelta(days=config.RETENCAO_CONTEUDO_DIAS) - timedelta(microseconds=1)
        )
        service.purgar(self.db)
        self.assertIsNotNone(self.db.get(Avaliacao, self.a.id))
        self.relogio.return_value += timedelta(microseconds=1)
        aid, cid = self.a.id, self.c.id
        service.purgar(self.db)
        self.db.expire_all()
        self.assertIsNone(self.db.get(Avaliacao, aid))
        self.assertIsNone(self.db.get(ComentarioVersao, cid))
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Denuncia)), 0)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Agradecimento)), 0)
        self.assertEqual(service.purgar(self.db), 0)

    def test_conta_minima_sem_login_tokens_ou_recadastro(self):
        for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
            self.db.add(
                modelo(
                    usuario_id=self.u.id,
                    token_hash=secrets.token_hex(32),
                    expires_at=self.agora + timedelta(days=1),
                )
            )
        self.db.commit()
        service.excluir_conta(self.db, self.u)
        self.db.expire_all()
        self.assertEqual(self.u.estado, "EXCLUIDA")
        self.assertEqual(self.u.nome, "")
        self.assertIsNone(self.u.password_hash)
        self.assertIsNone(self.u.termos_versao)
        self.assertIsNone(self.u.termos_ciencia_em)
        for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
            self.assertEqual(
                self.db.scalar(
                    select(func.count()).select_from(modelo).where(modelo.usuario_id == self.u.id)
                ),
                0,
            )
        with self.assertRaises(auth_service.CredenciaisInvalidasError):
            auth_service.autenticar(self.db, LoginRequest(email=self.email, senha=self.senha))
        from tests.auth_http_fixtures import TransporteEmMemoria

        sender = TransporteEmMemoria()
        auth_service.cadastrar(
            self.db,
            CadastroRequest(
                nome="Novo",
                email=self.email,
                senha=self.senha,
                ciencia_termos=True,
                termos_versao="2026-11-17",
            ),
            sender,
        )
        auth_service.solicitar_recuperacao_senha(self.db, self.email, sender)
        auth_service.reenviar_confirmacao(self.db, self.email, sender)
        self.assertEqual(sender.envios, [])
        self.assertIsNotNone(self.db.get(Avaliacao, self.a.id).excluido_em)

    def test_exclusao_sem_permissao_e_rollback(self):
        with self.assertRaises(HTTPException) as erro:
            service.excluir_avaliacao(self.db, self.mod, self.a.id)
        self.assertEqual(erro.exception.status_code, 404)
        with patch.object(repo, "remover_credenciais", side_effect=RuntimeError("sintetico")):
            with self.assertRaises(RuntimeError):
                service.excluir_conta(self.db, self.u)
        self.db.expire_all()
        self.assertIsNone(self.u.excluido_em)
        self.assertIsNone(self.a.excluido_em)

    def test_rejeicao_preserva_metadados_e_descarta_texto(self):
        from app.services import moderacao_service
        from app.schemas.moderacao import AcaoModeracaoRequest

        self.c.estado = EstadoComentario.PENDENTE
        self.db.commit()
        moderacao_service.decidir(
            self.db, self.mod, self.c.id, AcaoModeracaoRequest(acao="REJEITAR", motivo="SPAM")
        )
        self.db.expire_all()
        self.assertIsNone(self.c.texto)
        moderacao_repository.descartar_vencidos(self.db, self.agora + timedelta(days=100))
        self.db.commit()
        self.assertIsNotNone(
            self.db.scalar(
                select(DecisaoModeracao).where(DecisaoModeracao.comentario_versao_id == self.c.id)
            )
        )

    def test_endpoints_exclusao_exigem_sessao_e_csrf(self):
        for rota in (
            "/api/auth/conta",
            f"/api/avaliacoes/{self.a.id}",
            f"/api/moderacao/avaliacoes/{self.a.id}",
        ):
            self.assertEqual(self.client.delete(rota).status_code, 401)
        auth = auth_service.autenticar(self.db, LoginRequest(email=self.email, senha=self.senha))
        self.client.cookies.set("undb_session", auth.token)
        self.assertEqual(
            self.client.delete(
                "/api/auth/conta", headers={"Origin": "https://invalida.example"}
            ).status_code,
            403,
        )
        self.assertEqual(self.client.delete("/api/auth/conta").status_code, 204)
        self.assertFalse(self.client.get("/api/auth/sessao").json()["autenticado"])


class RetencaoTest(Casos, AuthHttpFixture, unittest.TestCase):
    pass


@unittest.skipUnless(
    os.environ.get("ABUSO_POSTGRES_TEST_URL"), "Exige PostgreSQL descartável migrado."
)
class RetencaoPostgresTest(Casos, AuthHttpFixture, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from sqlalchemy.engine import make_url

        url = make_url(os.environ["ABUSO_POSTGRES_TEST_URL"])
        if url.host not in {"localhost", "127.0.0.1", "::1"} or url.database not in {
            "undb_266_test",
            "ci",
        }:
            raise ValueError("Somente banco descartável local.")
        cls.pg_engine = engine_ensaio(url)

    @classmethod
    def tearDownClass(cls):
        cls.pg_engine.dispose()
