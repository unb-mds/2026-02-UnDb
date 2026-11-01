import unittest
import asyncio
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from tests import test_comentario as comentarios
from app.models.enums import EstadoComentario, MotivoDenuncia
from app.repositories import denuncia_repository
from tests import test_moderacao as moderacao


class PersistenciaDenunciaTest(unittest.TestCase):
    setUp = comentarios.ComentarioHttpIntegrationTest.setUp
    tearDown = comentarios.ComentarioHttpIntegrationTest.tearDown
    _criar_avaliacao_com_comentario = comentarios.ComentarioHttpIntegrationTest._criar_avaliacao_com_comentario
    _obter_comentario = comentarios.ComentarioHttpIntegrationTest._obter_comentario

    def test_unicidade_contas_visitantes_e_encerramento(self):
        avaliacao = self._criar_avaliacao_com_comentario(self.usuario, "texto", EstadoComentario.PUBLICADO)
        versao = self._obter_comentario(avaliacao.id)
        agora = datetime.now(timezone.utc)
        denuncia_repository.criar(self.db, versao.id, self.outro_usuario.id, MotivoDenuncia.SPAM, agora)
        with self.assertRaises(IntegrityError):
            with self.db.begin_nested():
                denuncia_repository.criar(self.db, versao.id, self.outro_usuario.id, MotivoDenuncia.SPAM, agora)
        for _ in range(3):
            denuncia_repository.criar(self.db, versao.id, None, MotivoDenuncia.SPAM, agora)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 1)
        self.assertEqual(len(denuncia_repository.listar(self.db, versao.id)), 4)
        denuncia_repository.encerrar(self.db, versao.id, "MANTIDO")
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 0)
        self.assertEqual(denuncia_repository.listar(self.db, versao.id), [])


class DenunciaHttpTest(unittest.TestCase):
    setUp = comentarios.ComentarioHttpIntegrationTest.setUp
    tearDown = comentarios.ComentarioHttpIntegrationTest.tearDown
    _request = staticmethod(comentarios.ComentarioHttpIntegrationTest._request)
    _criar_avaliacao_com_comentario = comentarios.ComentarioHttpIntegrationTest._criar_avaliacao_com_comentario
    _obter_comentario = comentarios.ComentarioHttpIntegrationTest._obter_comentario
    versao = moderacao.ModeracaoTest.versao
    moderador = moderacao.ModeracaoTest.moderador
    acao = moderacao.ModeracaoTest.acao

    def denunciar(self, versao_id, token=None, payload=None):
        return asyncio.run(self._request("POST", f"/api/comentarios/{versao_id}/denuncias",
                                        payload if payload is not None else {"motivo": "SPAM"}, token))

    def test_visitante_conta_nao_confirmada_duplicidade_e_privacidade(self):
        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        for _ in range(2):
            self.assertEqual(self.denunciar(versao.id)[0], 201)
        code, resultado = self.denunciar(versao.id, self.token_nao_confirmado)
        self.assertEqual(code, 201, resultado)
        self.assertEqual(set(resultado), {"mensagem"})
        self.assertEqual(self.denunciar(versao.id, self.token_nao_confirmado)[0], 409)
        caminho = f"/api/moderacao/comentarios/{versao.id}/denuncias"
        self.assertEqual(asyncio.run(self._request("GET", caminho))[0], 401)
        self.assertEqual(asyncio.run(self._request("GET", caminho, token=self.token))[0], 403)
        code, resultado = asyncio.run(self._request("GET", caminho, token="mod"))
        self.assertEqual(code, 200)
        self.assertEqual(resultado["contas_distintas"], 1)
        self.assertEqual(resultado["total_visitantes"], 2)
        self.assertEqual(resultado["autenticadas"][0]["denunciante"]["email"], self.usuario_nao_confirmado.email)

    def test_alvo_nao_publicado_inexistente_estruturado_e_schema(self):
        from uuid import uuid4
        versao = self.versao()
        self.assertEqual(self.denunciar(versao.id)[0], 404)
        self.assertEqual(self.denunciar(versao.avaliacao_id)[0], 404)
        self.assertEqual(self.denunciar(uuid4())[0], 404)
        versao.estado = EstadoComentario.PUBLICADO
        self.db.commit()
        for payload in ({}, {"motivo": "outro"}, {"motivo": "SPAM", "denunciante_id": str(self.usuario.id)}):
            self.assertEqual(self.denunciar(versao.id, payload=payload)[0], 422)
        self.assertEqual(denuncia_repository.listar(self.db, versao.id), [])

    def test_50_contas_suspendem_visitantes_nao_contam_e_suspenso_recusa(self):
        from app.models.usuario import Usuario
        from app.schemas.denuncia import DenunciaCreate
        from app.services import denuncia_service
        versao = self.versao(EstadoComentario.PUBLICADO)
        for _ in range(51):
            self.assertEqual(self.denunciar(versao.id)[0], 201)
        for i in range(49):
            usuario = Usuario(nome=f"Conta {i}", email=f"conta{i}@aluno.unb.br", password_hash="teste", email_confirmado=False)
            self.db.add(usuario)
            self.db.commit()
            denuncia_service.registrar(self.db, versao.id, usuario, DenunciaCreate(motivo="SPAM"))
        self.db.refresh(versao)
        self.assertEqual(versao.estado, EstadoComentario.PUBLICADO)
        self.assertEqual(self.denunciar(versao.id, self.token_nao_confirmado)[0], 201)
        self.db.refresh(versao)
        self.assertEqual(versao.estado, EstadoComentario.SUSPENSO)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 50)
        self.assertEqual(self.denunciar(versao.id)[0], 404)
        code, publicos = asyncio.run(self._request("GET", f"/api/professores/{self.professor.id}/disciplinas/{self.disciplina.id}/comentarios"))
        self.assertEqual(code, 200)
        self.assertEqual(publicos, [])
        code, mensagens = asyncio.run(self._request("GET", "/api/agradecimentos", token=self.token_nao_confirmado))
        self.assertEqual(code, 200)
        self.assertEqual(len(mensagens), 1)
        self.assertEqual(set(mensagens[0]), {"id", "mensagem"})
        self.assertEqual(asyncio.run(self._request("POST", f"/api/agradecimentos/{mensagens[0]['id']}/exibido", token=self.token))[0], 404)
        self.assertEqual(len(asyncio.run(self._request("GET", "/api/agradecimentos", token=self.token_nao_confirmado))[1]), 1)
        # The existing ASGI helper expects JSON; exercise the 204 through the service.
        denuncia_service.confirmar_exibicao(self.db, self.usuario_nao_confirmado, __import__('uuid').UUID(mensagens[0]['id']))
        self.assertEqual(asyncio.run(self._request("GET", "/api/agradecimentos", token=self.token_nao_confirmado))[1], [])
