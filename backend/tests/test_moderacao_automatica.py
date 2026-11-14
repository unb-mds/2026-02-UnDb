import asyncio
import unittest
from unittest.mock import patch
from sqlalchemy import select, func
from tests import test_triagem as triagem
from app.core import config
from app.models.comentario_versao import ComentarioVersao
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.enums import EstadoComentario as Estado
from app.schemas.triagem import ClassificacaoIA
from app.services import moderacao_automatica_service as auto, openai_triagem
from app.services.triagem_service import LimiteChamadas


class AutomaticaTest(unittest.TestCase):
    setUp = triagem.HttpTest.setUp
    tearDown = triagem.HttpTest.tearDown
    _request = staticmethod(triagem.HttpTest._request)
    _criar_avaliacao_com_comentario = triagem.HttpTest._criar_avaliacao_com_comentario
    _obter_comentario = triagem.HttpTest._obter_comentario

    def ativar(self):
        for nome, valor in {
            "MODERACAO_AUTOMATICA_ATIVA": True,
            "MODERACAO_FILTRO_ATIVO": True,
            "MODERACAO_IA_ATIVA": True,
            "MODERACAO_IA_DADOS_APROVADOS": True,
            "OPENAI_API_KEY": "teste",
        }.items():
            p = patch.object(config, nome, valor)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(auto, "limite", LimiteChamadas())
        p.start()
        self.addCleanup(p.stop)

    def enviar(self, texto="As explicações foram claras."):
        return asyncio.run(
            self._request(
                "POST", "/api/avaliacoes", {**self._payload, "comentario": texto}, self.token
            )
        )

    def limpo(self):
        return ClassificacaoIA(categorias=[], sinalizado=False, modelo="omni-moderation-latest")

    def test_publica_e_audita_sistema(self):
        self.ativar()
        with patch.object(openai_triagem, "classificar", return_value=self.limpo()):
            code, r = self.enviar()
        self.assertEqual(code, 200, r)
        self.assertEqual(r["comentario_estado"], "PUBLICADO")
        versao = self.db.scalar(select(ComentarioVersao))
        self.assertEqual(versao.estado, Estado.PUBLICADO)
        audit = self.db.scalar(select(DecisaoModeracao))
        self.assertIsNone(audit.moderador_id)
        self.assertEqual(audit.acao, "APROVAR")
        self.assertNotIn(versao.texto, audit.motivo)
        self.assertEqual(versao.avaliacao.didatica, 4)

    def test_sinais_e_falhas_pendentes(self):
        self.ativar()
        for resultado in (
            ClassificacaoIA(
                categorias=["harassment"], sinalizado=True, modelo="omni-moderation-latest"
            ),
            ClassificacaoIA(categorias=["hate"], sinalizado=False, modelo="omni-moderation-latest"),
            openai_triagem.TriagemIndisponivel(),
            TimeoutError(),
        ):
            opcoes = (
                {"side_effect": resultado}
                if isinstance(resultado, Exception)
                else {"return_value": resultado}
            )
            with patch.object(openai_triagem, "classificar", **opcoes):
                code, r = self.enviar()
            self.assertEqual(code, 200, r)
            self.assertEqual(r["comentario_estado"], "PENDENTE")
        self.assertEqual(self.db.scalar(select(func.count()).select_from(DecisaoModeracao)), 0)

    def test_filtro_privacidade_e_citacao_nao_enviam(self):
        self.ativar()
        for texto in (
            "Esse professor é um idiota.",
            "Telefone 61999991234",
            "Ele disse idiota; achei ruim.",
        ):
            with patch.object(openai_triagem, "classificar") as chamada:
                code, r = self.enviar(texto)
                self.assertEqual(code, 200, r)
                self.assertEqual(r["comentario_estado"], "PENDENTE")
                chamada.assert_not_called()

    def test_flags_obrigatorias(self):
        self.ativar()
        for flag in (
            "MODERACAO_AUTOMATICA_ATIVA",
            "MODERACAO_FILTRO_ATIVO",
            "MODERACAO_IA_ATIVA",
            "MODERACAO_IA_DADOS_APROVADOS",
        ):
            with (
                patch.object(config, flag, False),
                patch.object(openai_triagem, "classificar") as chamada,
            ):
                self.assertEqual(self.enviar()[1]["comentario_estado"], "PENDENTE")
                chamada.assert_not_called()

    def test_limite(self):
        self.ativar()
        with (
            patch.object(auto.limite, "reservar", return_value=False),
            patch.object(openai_triagem, "classificar") as chamada,
        ):
            code, r = self.enviar()
        self.assertEqual(code, 200, r)
        self.assertEqual(r["comentario_estado"], "PENDENTE")
        chamada.assert_not_called()

    def test_substituicao_limpa(self):
        self.ativar()
        with patch.object(openai_triagem, "classificar", return_value=self.limpo()):
            self.enviar("A aula foi clara.")
            anterior = self.db.scalar(select(ComentarioVersao))
            self.enviar("O material também foi claro.")
        self.db.expire_all()
        self.assertEqual(anterior.estado, Estado.SUBSTITUIDO)
        self.assertIsNone(anterior.texto)
        self.assertEqual(
            len(
                self.db.scalars(
                    select(ComentarioVersao).where(ComentarioVersao.estado == Estado.PUBLICADO)
                ).all()
            ),
            1,
        )

    def test_edicao_sinalizada_preserva_anterior(self):
        self.ativar()
        with patch.object(openai_triagem, "classificar", return_value=self.limpo()):
            self.enviar()
            anterior = self.db.scalar(select(ComentarioVersao))
            self.enviar("Que porra de aula.")
        self.db.expire_all()
        self.assertEqual(anterior.estado, Estado.PUBLICADO)
        self.assertIsNotNone(anterior.texto)

    def test_edicao_nao_contorna_suspensao(self):
        self.ativar()
        with patch.object(openai_triagem, "classificar", return_value=self.limpo()):
            self.enviar()
            anterior = self.db.scalar(select(ComentarioVersao))
            anterior.estado = Estado.SUSPENSO
            self.db.commit()
            self.assertEqual(
                self.enviar("Novo texto adequado.")[1]["comentario_estado"], "PENDENTE"
            )
        self.db.expire_all()
        self.assertEqual(anterior.estado, Estado.SUSPENSO)

    def test_retirada_durante_analise(self):
        self.ativar()

        def retirar(*args, **kwargs):
            versao = self.db.scalar(
                select(ComentarioVersao).where(ComentarioVersao.estado == Estado.PENDENTE)
            )
            versao.estado = Estado.RETIRADO
            self.db.commit()
            return self.limpo()

        with patch.object(openai_triagem, "classificar", side_effect=retirar):
            code, r = self.enviar()
        self.assertEqual(code, 200, r)
        self.assertIsNone(r["comentario_estado"])
        self.assertEqual(self.db.scalar(select(ComentarioVersao)).estado, Estado.RETIRADO)

    def test_erro_auditoria_nao_perde_criterios(self):
        self.ativar()
        with (
            patch.object(openai_triagem, "classificar", return_value=self.limpo()),
            patch.object(
                auto.moderacao_repository, "registrar_decisao", side_effect=RuntimeError("fixture")
            ),
        ):
            code, r = self.enviar()
        self.assertEqual(code, 200, r)
        self.assertEqual(r["comentario_estado"], "PENDENTE")
        self.db.expire_all()
        versao = self.db.scalar(select(ComentarioVersao))
        self.assertEqual(versao.estado, Estado.PENDENTE)
        self.assertEqual(versao.avaliacao.didatica, 4)
