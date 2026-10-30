"""Testes de integracao para endpoints de comentarios (RF20 / issue #156)."""

import asyncio
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+pysqlite:///:memory:",
)
os.environ.setdefault("SECRET_KEY", "teste-local")

from app.core.auth import SESSION_COOKIE_NAME
from app.core.database import Base, get_db
from app.core.security import gerar_hash_token
from app.main import app
from app.models.avaliacao import Avaliacao
from app.models.comentario_versao import ComentarioVersao
from app.models.disciplina import Disciplina
from app.models.enums import EstadoComentario
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.turma import Turma
from app.models.unidade import Unidade
from app.models.usuario import Usuario


class ComentarioHttpIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        self.usuario = Usuario(
            nome="Maria",
            email="maria.com@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=True,
        )
        self.usuario_nao_confirmado = Usuario(
            nome="Ana",
            email="ana.com@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=False,
        )
        self.outro_usuario = Usuario(
            nome="Pedro",
            email="pedro.com@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=True,
        )
        self.professor = Professor(
            nome="Professora Comentarios", departamento="CIC"
        )
        self.disciplina = Disciplina(
            codigo="CIC0098",
            nome="Disciplina Comentarios",
            departamento="CIC",
        )
        self.unidade = Unidade(codigo="CIC", nome="CIC")

        self.db.add_all(
            (
                self.usuario,
                self.usuario_nao_confirmado,
                self.outro_usuario,
                self.professor,
                self.disciplina,
                self.unidade,
            )
        )
        self.db.flush()
        self.db.add(
            Turma(
                disciplina=self.disciplina,
                unidade=self.unidade,
                codigo="01",
                semestre="2026.2",
                professores=[self.professor],
            )
        )

        self.token = "token-confirmado"
        self.token_nao_confirmado = "token-nao-confirmado"
        self.token_outro = "token-outro"
        expiracao = datetime.now(timezone.utc) + timedelta(days=1)
        self.db.add_all(
            (
                SessaoUsuario(
                    usuario_id=self.usuario.id,
                    token_hash=gerar_hash_token(self.token),
                    expires_at=expiracao,
                ),
                SessaoUsuario(
                    usuario_id=self.usuario_nao_confirmado.id,
                    token_hash=gerar_hash_token(self.token_nao_confirmado),
                    expires_at=expiracao,
                ),
                SessaoUsuario(
                    usuario_id=self.outro_usuario.id,
                    token_hash=gerar_hash_token(self.token_outro),
                    expires_at=expiracao,
                ),
            )
        )
        self.db.commit()

        self._payload = {
            "professor_id": str(self.professor.id),
            "disciplina_id": str(self.disciplina.id),
            "didatica": 4,
            "dificuldade": "MEDIO",
            "chamada": True,
            "disponibiliza_material": True,
            "qualidade_material": "BOM",
            "recomenda": True,
        }

        def override_get_db():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db

    def tearDown(self) -> None:
        app.dependency_overrides.pop(get_db, None)
        self.db.close()
        self.engine.dispose()

    @staticmethod
    async def _request(
        method: str,
        path: str,
        payload: dict | None = None,
        token: str | None = None,
    ) -> tuple[int, dict]:
        corpo = json.dumps(payload).encode("utf-8") if payload else b""
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(corpo)).encode("ascii")),
        ]
        if token is not None:
            headers.append(
                (b"cookie", f"{SESSION_COOKIE_NAME}={token}".encode("ascii"))
            )

        recebido = False

        async def receive():
            nonlocal recebido
            if recebido:
                return {"type": "http.disconnect"}
            recebido = True
            return {"type": "http.request", "body": corpo, "more_body": False}

        mensagens = []

        async def send(message):
            mensagens.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": method,
                "scheme": "http",
                "path": path,
                "raw_path": path.encode("ascii"),
                "query_string": b"",
                "headers": headers,
                "client": ("127.0.0.1", 12345),
                "server": ("testserver", 80),
                "root_path": "",
                "state": {},
            },
            receive,
            send,
        )
        inicio = next(
            mensagem
            for mensagem in mensagens
            if mensagem["type"] == "http.response.start"
        )
        resposta = b"".join(
            mensagem.get("body", b"")
            for mensagem in mensagens
            if mensagem["type"] == "http.response.body"
        )
        return inicio["status"], json.loads(resposta)

    def _criar_avaliacao_com_comentario(
        self,
        usuario: Usuario,
        texto: str,
        estado: EstadoComentario = EstadoComentario.PENDENTE,
    ) -> Avaliacao:
        avaliacao = Avaliacao(
            usuario_id=usuario.id,
            professor_id=self.professor.id,
            disciplina_id=self.disciplina.id,
            didatica=4,
            dificuldade="MEDIO",
            chamada=True,
            disponibiliza_material=True,
            qualidade_material="BOM",
            recomenda=True,
        )
        self.db.add(avaliacao)
        self.db.flush()
        self.db.add(
            ComentarioVersao(
                avaliacao_id=avaliacao.id,
                texto=texto,
                estado=estado,
            )
        )
        self.db.commit()
        return avaliacao

    def _obter_comentario(self, avaliacao_id):
        self.db.expire_all()
        return self.db.scalar(
            select(ComentarioVersao).where(
                ComentarioVersao.avaliacao_id == avaliacao_id
            )
        )

    # --- AC20-03: Leitura publica (visitante) ---

    def test_ac20_03_visitante_le_comentarios_publicados(self) -> None:
        self._criar_avaliacao_com_comentario(
            self.usuario, "texto publicado", EstadoComentario.PUBLICADO
        )

        status_code, resposta = asyncio.run(
            self._request(
                "GET",
                f"/api/professores/{self.professor.id}"
                f"/disciplinas/{self.disciplina.id}/comentarios",
            )
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(len(resposta), 1)
        self.assertEqual(resposta[0]["texto"], "texto publicado")
        self.assertNotIn("estado", resposta[0])
        self.assertNotIn("avaliacao_id", resposta[0])
        self.assertNotIn("substitui_id", resposta[0])
        self.assertNotIn("usuario_id", resposta[0])

    def test_ac20_03_visitante_nao_ve_comentarios_pendentes(self) -> None:
        self._criar_avaliacao_com_comentario(
            self.usuario, "texto pendente", EstadoComentario.PENDENTE
        )

        status_code, resposta = asyncio.run(
            self._request(
                "GET",
                f"/api/professores/{self.professor.id}"
                f"/disciplinas/{self.disciplina.id}/comentarios",
            )
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(resposta, [])

    def test_ac20_03_visitante_nao_ve_estado_ou_identidade(self) -> None:
        self._criar_avaliacao_com_comentario(
            self.usuario, "texto publicado", EstadoComentario.PUBLICADO
        )

        status_code, resposta = asyncio.run(
            self._request(
                "GET",
                f"/api/professores/{self.professor.id}"
                f"/disciplinas/{self.disciplina.id}/comentarios",
            )
        )

        self.assertEqual(status_code, 200)
        self.assertNotIn("usuario_id", resposta[0])
        self.assertNotIn("email", resposta[0])
        self.assertNotIn("estado", resposta[0])
        self.assertNotIn("substitui_id", resposta[0])

    def test_ac20_03_404_professor_inexistente(self) -> None:
        status_code, resposta = asyncio.run(
            self._request(
                "GET",
                f"/api/professores/{uuid4()}"
                f"/disciplinas/{self.disciplina.id}/comentarios",
            )
        )
        self.assertEqual(status_code, 404)
        self.assertIn("professor", resposta["detail"])

    def test_ac20_03_404_disciplina_inexistente(self) -> None:
        status_code, resposta = asyncio.run(
            self._request(
                "GET",
                f"/api/professores/{self.professor.id}"
                f"/disciplinas/{uuid4()}/comentarios",
            )
        )
        self.assertEqual(status_code, 404)
        self.assertIn("disciplina", resposta["detail"])

    # --- AC20-04: Acompanhamento pelo autor ---

    def test_ac20_04_autor_ve_comentarios_com_estado(self) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "meu comentario", EstadoComentario.PENDENTE
        )

        status_code, resposta = asyncio.run(
            self._request("GET", "/api/comentarios/meu", token=self.token)
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(len(resposta), 1)
        self.assertEqual(resposta[0]["texto"], "meu comentario")
        self.assertEqual(resposta[0]["estado"], "PENDENTE")
        self.assertEqual(resposta[0]["avaliacao_id"], str(avaliacao.id))

    def test_ac20_04_autor_nao_ve_comentarios_de_outros(self) -> None:
        self._criar_avaliacao_com_comentario(
            self.usuario, "comentario de maria", EstadoComentario.PENDENTE
        )
        self._criar_avaliacao_com_comentario(
            self.outro_usuario, "comentario de pedro", EstadoComentario.PENDENTE
        )

        status_code, resposta = asyncio.run(
            self._request("GET", "/api/comentarios/meu", token=self.token)
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(len(resposta), 1)
        self.assertEqual(resposta[0]["texto"], "comentario de maria")

    def test_ac20_04_exige_sessao_valida(self) -> None:
        status_code, resposta = asyncio.run(
            self._request("GET", "/api/comentarios/meu")
        )
        self.assertEqual(status_code, 401)
        self.assertIn("Sessão", resposta["detail"])

    def test_ac20_04_bloqueia_email_nao_confirmado(self) -> None:
        status_code, resposta = asyncio.run(
            self._request(
                "GET", "/api/comentarios/meu", token=self.token_nao_confirmado
            )
        )
        self.assertEqual(status_code, 403)
        self.assertIn("Confirme seu e-mail", resposta["detail"])

    # --- AC20-05: Retirada pelo autor ---

    def test_ac20_05_autor_retira_comentario_pendente(self) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "comentario a retirar", EstadoComentario.PENDENTE
        )
        comentario = self._obter_comentario(avaliacao.id)
        comentario_id = comentario.id

        status_code, resposta = asyncio.run(
            self._request(
                "PATCH",
                f"/api/comentarios/{comentario_id}/retirar",
                token=self.token,
            )
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(resposta["estado"], "RETIRADO")
        self.db.expire_all()
        comentario = self.db.get(ComentarioVersao, comentario_id)
        self.assertEqual(comentario.estado, EstadoComentario.RETIRADO)

    def test_ac20_05_autor_retira_comentario_suspenso(self) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "texto suspenso", EstadoComentario.SUSPENSO
        )
        comentario_id = self._obter_comentario(avaliacao.id).id
        criterios = (avaliacao.didatica, avaliacao.dificuldade, avaliacao.chamada,
                     avaliacao.disponibiliza_material, avaliacao.qualidade_material,
                     avaliacao.recomenda)

        status_code, resposta = asyncio.run(
            self._request(
                "PATCH", f"/api/comentarios/{comentario_id}/retirar", token=self.token
            )
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(resposta["estado"], "RETIRADO")
        self.db.expire_all()
        self.assertEqual(self.db.get(ComentarioVersao, comentario_id).estado,
                         EstadoComentario.RETIRADO)
        self.assertEqual((avaliacao.didatica, avaliacao.dificuldade, avaliacao.chamada,
                          avaliacao.disponibiliza_material, avaliacao.qualidade_material,
                          avaliacao.recomenda), criterios)

    def test_ac20_05_retirada_de_suspenso_cancela_substituto_pendente(self) -> None:
        self._verificar_retirada_cancela_substituto(EstadoComentario.SUSPENSO)

    def test_ac20_05_retirada_cancela_substituto_pendente(self) -> None:
        self._verificar_retirada_cancela_substituto(EstadoComentario.PUBLICADO)

    def _verificar_retirada_cancela_substituto(self, estado: EstadoComentario) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "texto anterior", estado
        )
        self.db.expire_all()
        publicado = self._obter_comentario(avaliacao.id)

        self.db.add(
            ComentarioVersao(
                avaliacao_id=avaliacao.id,
                texto="texto substituto",
                estado=EstadoComentario.PENDENTE,
                substitui_id=publicado.id,
            )
        )
        self.db.commit()
        self.db.expire_all()
        pendente = self.db.scalar(
            select(ComentarioVersao).where(
                ComentarioVersao.avaliacao_id == avaliacao.id,
                ComentarioVersao.estado == EstadoComentario.PENDENTE,
            )
        )
        pendente_id, publicado_id = pendente.id, publicado.id

        status_code, resposta = asyncio.run(
            self._request(
                "PATCH",
                f"/api/comentarios/{publicado_id}/retirar",
                token=self.token,
            )
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(resposta["estado"], "RETIRADO")
        self.db.expire_all()
        self.assertIsNone(self.db.get(ComentarioVersao, pendente_id))
        self.assertEqual(
            self.db.get(ComentarioVersao, publicado_id).estado,
            EstadoComentario.RETIRADO,
        )

    def test_ac20_05_exige_sessao_valida(self) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "comentario", EstadoComentario.PENDENTE
        )
        comentario = self._obter_comentario(avaliacao.id)

        status_code, resposta = asyncio.run(
            self._request(
                "PATCH", f"/api/comentarios/{comentario.id}/retirar"
            )
        )
        self.assertEqual(status_code, 401)
        self.assertIn("Sessão", resposta["detail"])

    def test_ac20_05_bloqueia_email_nao_confirmado(self) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "comentario", EstadoComentario.PENDENTE
        )
        comentario = self._obter_comentario(avaliacao.id)

        status_code, resposta = asyncio.run(
            self._request(
                "PATCH",
                f"/api/comentarios/{comentario.id}/retirar",
                token=self.token_nao_confirmado,
            )
        )
        self.assertEqual(status_code, 403)
        self.assertIn("Confirme seu e-mail", resposta["detail"])

    def test_ac20_05_403_alheio_nao_pode_retirar(self) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "comentario de maria", EstadoComentario.PENDENTE
        )
        comentario = self._obter_comentario(avaliacao.id)

        status_code, resposta = asyncio.run(
            self._request(
                "PATCH",
                f"/api/comentarios/{comentario.id}/retirar",
                token=self.token_outro,
            )
        )
        self.assertEqual(status_code, 403)

    def test_ac20_05_404_comentario_inexistente(self) -> None:
        status_code, resposta = asyncio.run(
            self._request(
                "PATCH",
                f"/api/comentarios/{uuid4()}/retirar",
                token=self.token,
            )
        )
        self.assertEqual(status_code, 404)
        self.assertIn("encontrado", resposta["detail"])

    def test_ac20_05_nao_retira_comentario_substituido(self) -> None:
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "texto substituido", EstadoComentario.SUBSTITUIDO
        )
        comentario = self._obter_comentario(avaliacao.id)

        status_code, resposta = asyncio.run(
            self._request(
                "PATCH",
                f"/api/comentarios/{comentario.id}/retirar",
                token=self.token,
            )
        )
        self.assertEqual(status_code, 403)
