import unittest
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from tests import test_comentario as comentarios
from app.models.enums import EstadoComentario, MotivoDenuncia
from app.repositories import denuncia_repository


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
