"""RF20/RF22 HTTP flows, using the existing comment integration fixture."""
import asyncio
import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from tests import test_comentario as comentarios
from app.core.security import gerar_hash_token
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.enums import EstadoComentario
from app.models.sessao_usuario import SessaoUsuario
from app.models.usuario import Usuario


class ModeracaoTest(unittest.TestCase):
    setUp = comentarios.ComentarioHttpIntegrationTest.setUp
    tearDown = comentarios.ComentarioHttpIntegrationTest.tearDown
    _request = staticmethod(comentarios.ComentarioHttpIntegrationTest._request)
    _criar_avaliacao_com_comentario = comentarios.ComentarioHttpIntegrationTest._criar_avaliacao_com_comentario
    _obter_comentario = comentarios.ComentarioHttpIntegrationTest._obter_comentario

    def moderador(self):
        usuario = Usuario(nome="Moderador", email="mod@aluno.unb.br", password_hash="teste",
                          email_confirmado=True, moderador=True)
        self.db.add(usuario)
        self.db.flush()
        self.db.add(SessaoUsuario(usuario_id=usuario.id, token_hash=gerar_hash_token("mod"),
                                 expires_at=datetime.now(timezone.utc) + timedelta(days=1)))
        self.db.commit()
        return usuario

    def versao(self, estado=EstadoComentario.PENDENTE, usuario=None):
        avaliacao = self._criar_avaliacao_com_comentario(usuario or self.usuario, "texto", estado)
        return self._obter_comentario(avaliacao.id)

    def acao(self, versao_id, acao, token="mod", motivo="revisao humana"):
        return asyncio.run(self._request("POST", f"/api/moderacao/comentarios/{versao_id}/acoes",
                                        {"acao": acao, "motivo": motivo}, token))

    def test_aprovar_publica_sem_denuncias_e_registra_decisao(self):
        moderador = self.moderador()
        versao = self.versao()
        code, resultado = self.acao(versao.id, "APROVAR")
        self.assertEqual(code, 200, resultado)
        self.assertEqual(resultado["estado_posterior"], "PUBLICADO")
        self.db.expire_all()
        self.assertEqual(versao.estado, EstadoComentario.PUBLICADO)
        decisao = self.db.scalar(select(DecisaoModeracao))
        self.assertEqual(decisao.moderador_id, moderador.id)
        self.assertEqual(decisao.motivo, "revisao humana")
        self.assertNotIn("texto", resultado)

    def test_rejeitar_descarta_texto_e_nao_altera_criterios(self):
        self.moderador()
        versao = self.versao()
        avaliacao_id = versao.avaliacao_id
        self.assertEqual(self.acao(versao.id, "REJEITAR")[0], 200)
        self.db.expire_all()
        self.assertEqual(versao.estado, EstadoComentario.REJEITADO)
        self.assertIsNone(versao.texto)
        self.assertEqual(versao.avaliacao.id, avaliacao_id)
        self.assertEqual(versao.avaliacao.didatica, 4)
        code, resultado = asyncio.run(self._request("GET", "/api/comentarios/meu", token=self.token))
        self.assertEqual(code, 200)
        self.assertIsNone(resultado[0]["texto"])

    def test_permissoes_e_impedimento_de_autoria(self):
        self.moderador()
        versao = self.versao()
        self.assertEqual(self.acao(versao.id, "APROVAR", None)[0], 401)
        self.assertEqual(self.acao(versao.id, "APROVAR", self.token)[0], 403)
        self.assertEqual(self.acao(versao.id, "APROVAR", self.token_nao_confirmado)[0], 403)
        self.usuario.moderador = True
        self.db.commit()
        self.assertEqual(self.acao(versao.id, "APROVAR", self.token)[0], 403)
        self.db.expire_all()
        self.assertEqual(versao.estado, EstadoComentario.PENDENTE)
        self.assertIsNone(self.db.scalar(select(DecisaoModeracao)))

    def test_transicao_invalida_e_motivo_obrigatorio(self):
        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        self.assertEqual(self.acao(versao.id, "APROVAR")[0], 409)
        self.assertEqual(self.acao(versao.id, "REJEITAR", motivo=" ")[0], 422)

    def test_fila_privada_e_filtro(self):
        self.moderador()
        self.versao()
        self.assertEqual(asyncio.run(self._request("GET", "/api/moderacao/comentarios"))[0], 401)
        code, fila = asyncio.run(self._request("GET", "/api/moderacao/comentarios", token="mod"))
        self.assertEqual(code, 200)
        self.assertEqual(fila[0]["autor"]["email"], self.usuario.email)


if __name__ == "__main__":
    unittest.main()
