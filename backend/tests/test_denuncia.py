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
        self.assertEqual(asyncio.run(self._request("POST", f"/api/agradecimentos/{mensagens[0]['id']}/exibido", token=self.token_nao_confirmado))[0], 204)
        self.assertEqual(asyncio.run(self._request("GET", "/api/agradecimentos", token=self.token_nao_confirmado))[1], [])

    def test_manter_encerra_e_permite_nova_denuncia_sem_contagem_herdada(self):
        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        self.assertEqual(self.denunciar(versao.id, self.token_nao_confirmado)[0], 201)
        self.assertEqual(self.acao(versao.id, "MANTER")[0], 200)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 0)
        self.assertEqual(self.denunciar(versao.id, self.token_nao_confirmado)[0], 201)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 1)

    def test_impedimento_denuncia_propria_preserva_caso(self):
        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        self.assertEqual(self.denunciar(versao.id, "mod")[0], 201)
        self.assertEqual(self.acao(versao.id, "REMOVER")[0], 403)
        self.db.refresh(versao)
        self.assertEqual(versao.estado, EstadoComentario.PUBLICADO)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 1)

    def test_remover_agradece_descarta_denuncias_e_nao_restaura(self):
        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        self.denunciar(versao.id, self.token_nao_confirmado)
        self.assertEqual(self.acao(versao.id, "REMOVER")[0], 200)
        self.db.refresh(versao)
        self.assertEqual(versao.estado, EstadoComentario.REMOVIDO)
        self.assertEqual(versao.texto, "texto")
        self.assertEqual(denuncia_repository.listar(self.db, versao.id), [])
        self.assertEqual(len(asyncio.run(self._request("GET", "/api/agradecimentos", token=self.token_nao_confirmado))[1]), 1)
        self.assertEqual(self.acao(versao.id, "RESTAURAR")[0], 409)

    def test_retirar_encerra_sem_agradecer_e_preserva_criterios(self):
        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        self.denunciar(versao.id, self.token_nao_confirmado)
        self.assertEqual(asyncio.run(self._request("PATCH", f"/api/comentarios/{versao.id}/retirar", token=self.token))[0], 200)
        self.db.refresh(versao)
        self.assertEqual(versao.estado, EstadoComentario.RETIRADO)
        self.assertEqual(versao.avaliacao.didatica, 4)
        self.assertEqual(denuncia_repository.listar(self.db, versao.id), [])
        self.assertEqual(asyncio.run(self._request("GET", "/api/agradecimentos", token=self.token_nao_confirmado))[1], [])

    def test_substituicao_de_suspenso_encerra_sem_transferir_denuncias(self):
        from app.models.comentario_versao import ComentarioVersao
        self.moderador()
        anterior = self.versao(EstadoComentario.PUBLICADO)
        self.denunciar(anterior.id, self.token_nao_confirmado)
        anterior.estado = EstadoComentario.SUSPENSO
        self.db.commit()
        payload = dict(self._payload, comentario="novo texto")
        self.assertEqual(asyncio.run(self._request("POST", "/api/avaliacoes", payload, self.token))[0], 200)
        self.db.expire_all()
        from sqlalchemy import select
        novo = self.db.scalar(select(ComentarioVersao).where(ComentarioVersao.estado == EstadoComentario.PENDENTE))
        self.assertEqual(novo.substitui_id, anterior.id)
        self.assertEqual(self.acao(novo.id, "APROVAR")[0], 200)
        self.db.refresh(anterior)
        self.assertIsNone(anterior.texto)
        self.assertEqual(anterior.estado, EstadoComentario.SUBSTITUIDO)
        self.assertEqual(denuncia_repository.listar(self.db, anterior.id), [])
        self.assertEqual(self.denunciar(anterior.id)[0], 404)
        self.assertEqual(denuncia_repository.contar_contas(self.db, novo.id), 0)
        self.assertEqual(self.denunciar(novo.id, self.token_nao_confirmado)[0], 201)

    def test_rejeitar_substituto_mantem_anterior_e_denuncias(self):
        from app.models.comentario_versao import ComentarioVersao
        self.moderador()
        anterior = self.versao(EstadoComentario.PUBLICADO)
        self.denunciar(anterior.id, self.token_nao_confirmado)
        novo = ComentarioVersao(avaliacao_id=anterior.avaliacao_id, substitui_id=anterior.id,
                                texto="substituto", estado=EstadoComentario.PENDENTE)
        self.db.add(novo)
        self.db.commit()
        self.assertEqual(self.acao(novo.id, "REJEITAR")[0], 200)
        self.db.refresh(anterior)
        self.assertEqual(anterior.estado, EstadoComentario.PUBLICADO)
        self.assertEqual(denuncia_repository.contar_contas(self.db, anterior.id), 1)

    def test_restaurar_encerra_sem_agradecimento_adicional(self):
        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        self.denunciar(versao.id, self.token_nao_confirmado)
        versao.estado = EstadoComentario.SUSPENSO
        self.db.commit()
        self.assertEqual(self.acao(versao.id, "RESTAURAR")[0], 200)
        self.db.refresh(versao)
        self.assertEqual(versao.estado, EstadoComentario.PUBLICADO)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 0)
        self.assertEqual(self.denunciar(versao.id, self.token_nao_confirmado)[0], 201)

    def test_retirar_substituto_tambem_retira_publicado_sem_agradecer(self):
        from app.models.comentario_versao import ComentarioVersao
        self.moderador()
        atual = self.versao(EstadoComentario.PUBLICADO)
        self.denunciar(atual.id, self.token_nao_confirmado)
        pendente = ComentarioVersao(avaliacao_id=atual.avaliacao_id, substitui_id=atual.id,
                                    texto="substituto", estado=EstadoComentario.PENDENTE)
        self.db.add(pendente)
        self.db.commit()
        self.assertEqual(asyncio.run(self._request("PATCH", f"/api/comentarios/{pendente.id}/retirar", token=self.token))[0], 200)
        self.db.refresh(atual)
        self.assertEqual(atual.estado, EstadoComentario.RETIRADO)
        self.assertEqual(denuncia_repository.listar(self.db, atual.id), [])
        self.assertEqual(self.acao(pendente.id, "APROVAR")[0], 409)
