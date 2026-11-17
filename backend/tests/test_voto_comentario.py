"""Regressões RF20/#278 com dados sintéticos e respostas sem identidades."""

import asyncio
import unittest
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models.comentario_versao import ComentarioVersao
from app.models.enums import EstadoComentario
from app.models.voto_comentario import VotoComentario
from app.models.denuncia import Denuncia
from app.repositories import moderacao_repository
from tests import test_comentario as fixture


class VotoComentarioTest(unittest.TestCase):
    setUp = fixture.ComentarioHttpIntegrationTest.setUp
    tearDown = fixture.ComentarioHttpIntegrationTest.tearDown
    _request = staticmethod(fixture.ComentarioHttpIntegrationTest._request)
    _criar_avaliacao_com_comentario = (
        fixture.ComentarioHttpIntegrationTest._criar_avaliacao_com_comentario
    )
    _obter_comentario = fixture.ComentarioHttpIntegrationTest._obter_comentario

    def preparar(self):
        avaliacao = self._criar_avaliacao_com_comentario(
            self.usuario, "Crítica acadêmica legítima", EstadoComentario.PUBLICADO
        )
        self.versao_id = self._obter_comentario(avaliacao.id).id
        return avaliacao

    def votar(self, voto, token="outro"):
        return asyncio.run(
            self._request(
                "POST",
                f"/api/comentarios/{self.versao_id}/voto",
                {"voto": voto},
                {
                    "outro": self.token_outro,
                    "autor": self.token,
                    "nao_confirmado": self.token_nao_confirmado,
                }.get(token),
            )
        )

    def consultar(self, token=None):
        return asyncio.run(
            self._request(
                "GET",
                f"/api/comentarios/{self.versao_id}/utilidade",
                token=token,
            )
        )

    def test_autorizacao_corpo_fechado_e_alvo_indisponivel(self):
        self.preparar()
        for token, status in [(None, 401), ("nao_confirmado", 403), ("autor", 403)]:
            self.assertEqual(self.votar("UTIL", token)[0], status)
        for corpo in [{"voto": "INVALIDO"}, {"voto": "UTIL", "usuario_id": str(uuid4())}, {}]:
            self.assertEqual(
                asyncio.run(
                    self._request(
                        "POST",
                        f"/api/comentarios/{self.versao_id}/voto",
                        corpo,
                        self.token_outro,
                    )
                )[0],
                422,
            )
        for estado in EstadoComentario:
            if estado == EstadoComentario.PUBLICADO:
                continue
            versao = self.db.get(ComentarioVersao, self.versao_id)
            versao.estado = estado
            self.db.commit()
            self.assertEqual(self.votar("UTIL"), (404, {"detail": "comentario indisponivel"}))
            self.assertEqual(self.consultar(), (404, {"detail": "comentario indisponivel"}))
        self.versao_id = uuid4()
        self.assertEqual(self.votar("UTIL"), (404, {"detail": "comentario indisponivel"}))

    def test_repeticao_troca_retirada_e_privacidade(self):
        self.preparar()
        for voto, esperado in [
            ("UTIL", (1, 0)),
            ("UTIL", (1, 0)),
            ("NAO_UTIL", (0, 1)),
            (None, (0, 0)),
            (None, (0, 0)),
        ]:
            status, resposta = self.votar(voto)
            self.assertEqual(status, 200)
            self.assertEqual(
                resposta, dict(uteis=esperado[0], nao_uteis=esperado[1], meu_voto=voto)
            )
        self.votar("UTIL")
        self.assertEqual(self.consultar(self.token_outro)[1]["meu_voto"], "UTIL")
        for token in [None, self.token, self.token_nao_confirmado]:
            self.assertEqual(
                self.consultar(token), (200, dict(uteis=1, nao_uteis=0, meu_voto=None))
            )
        self.assertEqual(self.db.scalar(select(func.count()).select_from(VotoComentario)), 1)
        self.db.add(
            VotoComentario(
                comentario_versao_id=self.versao_id, usuario_id=self.outro_usuario.id, voto="UTIL"
            )
        )
        with self.assertRaises(IntegrityError):
            self.db.flush()
        self.db.rollback()

    def test_isolamento_ordem_criterios_denuncias_e_publicacao(self):
        avaliacao = self.preparar()
        self._criar_avaliacao_com_comentario(
            self.outro_usuario, "Outro texto", EstadoComentario.PUBLICADO
        )
        path = f"/api/professores/{self.professor.id}/disciplinas/{self.disciplina.id}"
        antes = asyncio.run(self._request("GET", path))
        lista = asyncio.run(self._request("GET", path + "/comentarios"))
        criterios = (
            avaliacao.didatica,
            avaliacao.dificuldade,
            avaliacao.chamada,
            avaliacao.disponibiliza_material,
            avaliacao.qualidade_material,
            avaliacao.recomenda,
        )
        self.votar("NAO_UTIL")
        self.assertEqual(asyncio.run(self._request("GET", path)), antes)
        self.assertEqual(asyncio.run(self._request("GET", path + "/comentarios")), lista)
        self.db.expire_all()
        self.assertEqual(
            self.db.get(ComentarioVersao, self.versao_id).estado, EstadoComentario.PUBLICADO
        )
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Denuncia)), 0)
        self.assertEqual(
            (
                avaliacao.didatica,
                avaliacao.dificuldade,
                avaliacao.chamada,
                avaliacao.disponibiliza_material,
                avaliacao.qualidade_material,
                avaliacao.recomenda,
            ),
            criterios,
        )

    def test_retirada_e_descarte_no_prazo_da_versao(self):
        self.preparar()
        self.votar("UTIL")
        self.assertEqual(
            asyncio.run(
                self._request(
                    "PATCH",
                    f"/api/comentarios/{self.versao_id}/retirar",
                    token=self.token,
                )
            )[0],
            200,
        )
        self.assertEqual(self.votar("UTIL")[0], 404)
        self.db.expire_all()
        versao = self.db.get(ComentarioVersao, self.versao_id)
        prazo = versao.descartar_em
        moderacao_repository.descartar_vencidos(self.db, prazo - timedelta(seconds=1))
        self.assertEqual(self.db.scalar(select(func.count()).select_from(VotoComentario)), 1)
        moderacao_repository.descartar_vencidos(self.db, prazo)
        self.db.commit()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(VotoComentario)), 0)
        self.db.expire_all()
        self.assertIsNone(self.db.get(ComentarioVersao, self.versao_id))

    def test_substituto_sem_heranca_e_descarte_manual(self):
        self.preparar()
        self.votar("UTIL")
        from app.services import moderacao_service
        from app.schemas.moderacao import AcaoModeracaoRequest
        from app.models.enums import AcaoModeracao

        moderador = self.usuario_nao_confirmado
        moderador.email_confirmado = True
        moderador.moderador = True
        anterior = self.db.get(ComentarioVersao, self.versao_id)
        novo = ComentarioVersao(
            avaliacao_id=anterior.avaliacao_id,
            substitui_id=anterior.id,
            texto="Substituto",
            estado=EstadoComentario.PENDENTE,
        )
        self.db.add(novo)
        self.db.commit()
        moderacao_service.decidir(
            self.db,
            moderador,
            novo.id,
            AcaoModeracaoRequest(acao=AcaoModeracao.APROVAR, motivo="Texto adequado"),
        )
        self.assertEqual(self.consultar()[0], 404)
        self.versao_id = novo.id
        self.assertEqual(self.consultar()[1], dict(uteis=0, nao_uteis=0, meu_voto=None))
        self.assertEqual(self.db.scalar(select(func.count()).select_from(VotoComentario)), 0)

    def test_respostas_privadas_sem_cache_e_logs_sem_identidades(self):
        from unittest.mock import patch

        self.preparar()
        self.votar("UTIL")
        aplicacao = fixture.app
        headers = []

        async def capturar(scope, receive, send):
            async def enviar(mensagem):
                if mensagem["type"] == "http.response.start":
                    headers.append(dict(mensagem["headers"]))
                await send(mensagem)

            await aplicacao(scope, receive, enviar)

        with (
            patch.object(fixture, "app", capturar),
            self.assertLogs("app.http", level="INFO") as logs,
        ):
            self.consultar(self.token_outro)
            self.votar("UTIL", "autor")
        for h in headers:
            self.assertEqual(h[b"cache-control"], b"no-store")
            self.assertEqual(h[b"referrer-policy"], b"no-referrer")
        for valor in [
            str(self.versao_id),
            str(self.outro_usuario.id),
            self.outro_usuario.email,
            self.token_outro,
        ]:
            self.assertNotIn(valor, " ".join(logs.output))

    def test_substituicao_automatica_apaga_votos_sem_herdar(self):
        from contextlib import ExitStack
        from types import SimpleNamespace
        from unittest.mock import patch
        from app.services import moderacao_automatica_service as automatica

        self.preparar()
        self.votar("UTIL")
        anterior = self.db.get(ComentarioVersao, self.versao_id)
        novo = ComentarioVersao(
            avaliacao_id=anterior.avaliacao_id,
            substitui_id=anterior.id,
            texto="As aulas explicam o conteúdo",
            estado=EstadoComentario.PENDENTE,
        )
        self.db.add(novo)
        self.db.commit()
        novo_id = novo.id
        with ExitStack() as stack:
            for flag in [
                "MODERACAO_AUTOMATICA_ATIVA",
                "MODERACAO_FILTRO_ATIVO",
                "MODERACAO_IA_ATIVA",
                "MODERACAO_IA_DADOS_APROVADOS",
            ]:
                stack.enter_context(patch.object(automatica.config, flag, True))
            stack.enter_context(patch.object(automatica.config, "OPENAI_API_KEY", "synthetic"))
            stack.enter_context(patch.object(automatica.limite, "reservar", return_value=True))
            stack.enter_context(
                patch.object(
                    automatica.openai_triagem,
                    "classificar",
                    return_value=SimpleNamespace(
                        sinalizado=False, categorias=[], modelo="sintetico"
                    ),
                )
            )
            self.assertEqual(automatica.processar(self.db, novo_id), EstadoComentario.PUBLICADO)
        self.assertEqual(self.consultar()[0], 404)
        self.versao_id = novo_id
        self.assertEqual(self.consultar()[1], dict(uteis=0, nao_uteis=0, meu_voto=None))
        self.assertEqual(self.db.scalar(select(func.count()).select_from(VotoComentario)), 0)

    def test_suspensao_restauracao_preserva_votos_da_mesma_versao(self):
        self.preparar()
        self.votar("UTIL")
        versao = self.db.get(ComentarioVersao, self.versao_id)
        versao.estado = EstadoComentario.SUSPENSO
        self.db.commit()
        self.assertEqual(self.consultar()[0], 404)
        self.assertEqual(self.votar(None)[0], 404)
        versao.estado = EstadoComentario.PUBLICADO
        self.db.commit()
        self.assertEqual(
            self.consultar(self.token_outro)[1], dict(uteis=1, nao_uteis=0, meu_voto="UTIL")
        )
