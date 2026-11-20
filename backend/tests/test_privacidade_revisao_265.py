"""#265: fronteiras entre público, autor, denunciante e moderação; dados sintéticos."""

import asyncio
import unittest
from datetime import datetime, timedelta, timezone

from httpx import ASGITransport, AsyncClient

from app.core.security import gerar_hash_token
from app.main import app
from app.models.avaliacao import Avaliacao
from app.models.comentario_versao import ComentarioVersao
from app.models.enums import EstadoComentario
from app.models.sessao_usuario import SessaoUsuario
from app.models.usuario import Usuario
from tests import test_comentario as fixture


class PrivacidadeRevisaoTest(unittest.TestCase):
    setUp = fixture.ComentarioHttpIntegrationTest.setUp
    tearDown = fixture.ComentarioHttpIntegrationTest.tearDown
    _criar_avaliacao_com_comentario = (
        fixture.ComentarioHttpIntegrationTest._criar_avaliacao_com_comentario
    )
    _obter_comentario = fixture.ComentarioHttpIntegrationTest._obter_comentario

    def preparar(self):
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "Experiência sintética sem dados pessoais", EstadoComentario.PUBLICADO
        )
        self.versao = self._obter_comentario(avaliacao.id)
        self.avaliacao_id = avaliacao.id
        self.rota = f"/api/professores/{self.professor.id}/disciplinas/{self.disciplina.id}"
        moderador = Usuario(
            nome="Revisor sintético",
            email="privacidade.mod@aluno.unb.br",
            password_hash="hash-sintetico",
            email_confirmado=True,
            moderador=True,
        )
        self.db.add(moderador)
        self.db.flush()
        self.db.add(
            SessaoUsuario(
                usuario_id=moderador.id,
                token_hash=gerar_hash_token("revisor"),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            )
        )
        self.db.commit()

    def solicitar(self, path, token=None, *, method="GET", body=None):
        async def executar():
            async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
                headers = {"Origin": "http://localhost:3000"}
                if token:
                    headers["Cookie"] = f"undb_session={token}"
                return await client.request(method, path, headers=headers, json=body)

        return asyncio.run(executar())

    def test_respostas_publicas_tem_allowlist_sem_autoria_nem_denunciantes(self):
        self.preparar()
        denuncia = self.solicitar(
            f"/api/comentarios/{self.versao.id}/denuncias",
            self.token_outro,
            method="POST",
            body={"motivo": "OFENSA_PESSOAL"},
        )
        self.assertEqual(denuncia.status_code, 201)
        self.assertEqual(set(denuncia.json()), {"mensagem"})
        proibidos = [
            self.usuario.nome,
            self.usuario.email,
            str(self.usuario.id),
            self.outro_usuario.nome,
            self.outro_usuario.email,
            str(self.outro_usuario.id),
        ]
        for token in (None, self.token, self.token_outro, "revisor"):
            with self.subTest(token=token):
                resposta = self.solicitar(self.rota + "/comentarios", token)
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(set(resposta.json()[0]), {"id", "texto", "created_at"})
                for dado in proibidos:
                    self.assertNotIn(dado, resposta.text)
                agregado = self.solicitar(self.rota, token)
                self.assertEqual(agregado.status_code, 200)
                self.assertFalse(agregado.json()["dados_suficientes"])
                self.assertNotIn("didatica", agregado.json())
                for dado in proibidos:
                    self.assertNotIn(dado, agregado.text)

    def test_campos_internos_so_chegam_ao_moderador_autorizado(self):
        self.preparar()
        self.solicitar(
            f"/api/comentarios/{self.versao.id}/denuncias",
            self.token_outro,
            method="POST",
            body={"motivo": "OFENSA_PESSOAL"},
        )
        base = f"/api/moderacao/comentarios/{self.versao.id}"
        for path in (base, base + "/denuncias", base + "/decisoes"):
            for token, status in (
                (None, 401),
                (self.token, 403),
                (self.token_outro, 403),
                (self.token_nao_confirmado, 403),
            ):
                with self.subTest(path=path, token=token):
                    r = self.solicitar(path, token)
                    self.assertEqual(r.status_code, status)
                    self.assertEqual(r.headers["cache-control"], "no-store")
                    self.assertNotIn(self.usuario.email, r.text)
            r = self.solicitar(path, "revisor")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.headers["cache-control"], "no-store")
            self.assertEqual(r.headers["referrer-policy"], "no-referrer")
        autor = self.solicitar(base, "revisor").json()["autor"]
        self.assertEqual(set(autor), {"id", "nome", "email"})
        denunciante = self.solicitar(base + "/denuncias", "revisor").json()["autenticadas"][0][
            "denunciante"
        ]
        self.assertEqual(set(denunciante), {"id", "nome", "email"})
        self.assertEqual(denunciante["id"], str(self.outro_usuario.id))

    def test_contas_alternadas_nao_recebem_respostas_individuais_alheias(self):
        self.preparar()
        for token, quantidade in ((self.token, 1), (self.token_outro, 0), (self.token, 1)):
            for path in ("/api/comentarios/meu", "/api/avaliacoes/minhas"):
                r = self.solicitar(path + f"?usuario_id={self.usuario.id}", token)
                self.assertEqual(r.status_code, 200)
                dados = r.json()["itens"] if isinstance(r.json(), dict) else r.json()
                self.assertEqual(len(dados), quantidade)
                self.assertEqual(r.headers["cache-control"], "no-store")
                self.assertEqual(r.headers["referrer-policy"], "no-referrer")
        for path in (
            f"/api/comentarios/{self.versao.id}/retirar",
            f"/api/avaliacoes/{self.avaliacao_id}",
        ):
            r = self.solicitar(
                path, self.token_outro, method="PATCH" if path.endswith("retirar") else "DELETE"
            )
            self.assertIn(r.status_code, (403, 404))
        self.db.expire_all()
        self.assertEqual(
            self.db.get(ComentarioVersao, self.versao.id).estado, EstadoComentario.PUBLICADO
        )
        self.assertIsNone(self.db.get(Avaliacao, self.avaliacao_id).excluido_em)

    def test_utilidade_publica_so_inclui_contagens_e_voto_da_propria_sessao(self):
        self.preparar()
        path = f"/api/comentarios/{self.versao.id}"
        r = self.solicitar(path + "/voto", self.token_outro, method="POST", body={"voto": "UTIL"})
        self.assertEqual(r.status_code, 200)
        for token, voto in (
            (self.token_outro, "UTIL"),
            (None, None),
            (self.token, None),
            ("revisor", None),
        ):
            r = self.solicitar(path + "/utilidade", token)
            self.assertEqual(r.json(), {"uteis": 1, "nao_uteis": 0, "meu_voto": voto})
            self.assertEqual(r.headers["cache-control"], "no-store")
            self.assertEqual(r.headers["referrer-policy"], "no-referrer")
            self.assertNotIn(str(self.outro_usuario.id), r.text)

    def test_exclusao_logica_oculta_publico_privado_e_votos(self):
        self.preparar()
        r = self.solicitar(f"/api/avaliacoes/{self.avaliacao_id}", self.token, method="DELETE")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(self.solicitar(self.rota + "/comentarios").json(), [])
        self.assertEqual(self.solicitar(self.rota).json()["total_avaliacoes"], 0)
        self.assertEqual(self.solicitar("/api/avaliacoes/minhas", self.token).json()["itens"], [])
        self.assertEqual(
            self.solicitar(f"/api/comentarios/{self.versao.id}/utilidade").status_code, 404
        )
