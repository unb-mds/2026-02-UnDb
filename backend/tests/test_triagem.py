"""Issue #239: apoio assistivo e privacidade, sem chamadas externas."""

import asyncio
import json
import unittest
from unittest.mock import MagicMock, patch
from tests import test_moderacao as moderacao
from app.domain.triagem_comentario import categorias_lexicais, contem_dados_sensiveis
from app.models.enums import EstadoComentario
from app.schemas.triagem import CategoriaOpenAI, ClassificacaoIA
from app.services import openai_triagem, triagem_service


class LocalTest(unittest.TestCase):
    def test_palavras_completas_acentos_e_critica(self):
        self.assertEqual(categorias_lexicais("IDÍOTA!"), ["OFENSA_PESSOAL"])
        self.assertEqual(categorias_lexicais("idiotamente"), [])
        self.assertEqual(categorias_lexicais("didática ruim, provas difíceis; não recomendo"), [])
        self.assertEqual(categorias_lexicais("vou  te\nmatar"), ["AMEACA"])

    def test_privacidade(self):
        for texto in (
            "x@y.com",
            "x @ y.com",
            "(61) 99999-1234",
            "123.456.789-00",
            "matrícula 123",
            "senha abc",
            "https://x.com",
            "sk-segredo",
        ):
            self.assertTrue(contem_dados_sensiveis(texto), texto)
        self.assertTrue(contem_dados_sensiveis("Sou MáRia", ("Maria Silva",)))
        self.assertFalse(contem_dados_sensiveis("A didática não me ajudou"))

    def test_limites(self):
        limite = triagem_service.LimiteChamadas()
        self.assertFalse(limite.reservar(0, 10))
        with patch("app.services.triagem_service.monotonic", return_value=10):
            self.assertTrue(limite.reservar(1, 2))
            self.assertFalse(limite.reservar(1, 2))
        with patch("app.services.triagem_service.monotonic", return_value=80):
            self.assertTrue(limite.reservar(1, 2))
        with patch("app.services.triagem_service.monotonic", return_value=150):
            self.assertFalse(limite.reservar(1, 2))
        with patch("app.services.triagem_service.monotonic", return_value=90000):
            self.assertTrue(limite.reservar(1, 2))

    def test_cliente_payload_e_falhas(self):
        fake = MagicMock()
        resultado = {
            "flagged": True,
            "categories": {c.value: c == CategoriaOpenAI.HARASSMENT for c in CategoriaOpenAI},
        }
        resposta = {"id": "modr-teste", "model": "omni-moderation-latest", "results": [resultado]}

        def responder(valor):
            fake.open.return_value.__enter__.return_value.read.return_value = json.dumps(
                valor
            ).encode()

        responder(resposta)
        with patch("app.services.openai_triagem.build_opener", return_value=fake):
            r = openai_triagem.classificar(
                "Crítica", chave="segredo", modelo="omni-moderation-latest", timeout=2
            )
            self.assertTrue(r.sinalizado)
            self.assertEqual(r.categorias, [CategoriaOpenAI.HARASSMENT])
            req = fake.open.call_args.args[0]
            self.assertEqual(req.full_url, "https://api.openai.com/v1/moderations")
            self.assertEqual(
                json.loads(req.data), {"model": "omni-moderation-latest", "input": "Crítica"}
            )
            for dados in (
                {"results": []},
                {**resposta, "results": [resultado, resultado]},
                {
                    **resposta,
                    "results": [{"flagged": "false", "categories": resultado["categories"]}],
                },
                {**resposta, "results": [{"flagged": False, "categories": {"harassment": False}}]},
                {**resposta, "model": "gpt-pago"},
            ):
                responder(dados)
                with self.assertRaises(openai_triagem.TriagemIndisponivel):
                    openai_triagem.classificar(
                        "texto", chave="segredo", modelo="omni-moderation-latest", timeout=2
                    )
            chamadas = fake.open.call_count
            with self.assertRaises(openai_triagem.TriagemIndisponivel):
                openai_triagem.classificar("texto", chave="segredo", modelo="gpt-pago", timeout=2)
            self.assertEqual(fake.open.call_count, chamadas, "não pode chamar endpoint pago")
            fake.open.side_effect = TimeoutError("segredo e comentario")
            with self.assertRaises(openai_triagem.TriagemIndisponivel) as erro:
                openai_triagem.classificar(
                    "texto", chave="segredo", modelo="omni-moderation-latest", timeout=2
                )
            self.assertNotIn("segredo", str(erro.exception))


class HttpTest(unittest.TestCase):
    def setUp(self):
        moderacao.ModeracaoTest.setUp(self)
        from app.core import config

        # Testes não dependem do .env privado nem podem usar sua chave real.
        for nome, valor in {
            "MODERACAO_AUTOMATICA_ATIVA": False,
            "MODERACAO_FILTRO_ATIVO": False,
            "MODERACAO_IA_ATIVA": False,
            "MODERACAO_IA_DADOS_APROVADOS": False,
            "OPENAI_API_KEY": "",
        }.items():
            p = patch.object(config, nome, valor)
            p.start()
            self.addCleanup(p.stop)

    tearDown = moderacao.ModeracaoTest.tearDown
    _request = staticmethod(moderacao.ModeracaoTest._request)
    _criar_avaliacao_com_comentario = moderacao.ModeracaoTest._criar_avaliacao_com_comentario
    _obter_comentario = moderacao.ModeracaoTest._obter_comentario
    moderador = moderacao.ModeracaoTest.moderador
    versao = moderacao.ModeracaoTest.versao

    def triagem(self, versao, token="mod"):
        return asyncio.run(
            self._request("POST", f"/api/moderacao/comentarios/{versao.id}/triagem", token=token)
        )

    def ativar(self):
        from app.core import config

        for nome, valor in {
            "MODERACAO_IA_ATIVA": True,
            "MODERACAO_IA_DADOS_APROVADOS": True,
            "OPENAI_API_KEY": "segredo",
            "MODERACAO_FILTRO_ATIVO": True,
        }.items():
            p = patch.object(config, nome, valor)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(triagem_service, "limite", triagem_service.LimiteChamadas())
        p.start()
        self.addCleanup(p.stop)

    def test_permissoes(self):
        self.moderador()
        versao = self.versao()
        with patch.object(openai_triagem, "classificar") as chamada:
            for token, esperado in (
                (None, 401),
                (self.token, 403),
                (self.token_nao_confirmado, 403),
            ):
                self.assertEqual(self.triagem(versao, token)[0], esperado)
            self.usuario.moderador = True
            self.db.commit()
            self.assertEqual(self.triagem(versao, self.token)[0], 403)
            chamada.assert_not_called()

    def test_desativada(self):
        self.moderador()
        with patch.object(openai_triagem, "classificar") as chamada:
            code, r = self.triagem(self.versao())
        self.assertEqual(code, 200)
        self.assertEqual(r["status"], "DESATIVADA")
        self.assertEqual(r["categorias_locais"], [])
        chamada.assert_not_called()

    def test_analise_nao_altera_avaliacao(self):
        self.ativar()
        self.moderador()
        versao = self.versao()
        with patch.object(
            openai_triagem,
            "classificar",
            return_value=ClassificacaoIA(
                categorias=[], sinalizado=False, modelo="omni-moderation-latest"
            ),
        ) as chamada:
            code, r = self.triagem(versao)
        self.assertEqual(code, 200, r)
        self.assertEqual(r["status"], "CONCLUIDA")
        self.assertEqual(chamada.call_args.args, ("texto",))
        self.assertNotIn("autor", r)
        self.assertNotIn("texto", r)
        self.db.expire_all()
        self.assertEqual(versao.estado, EstadoComentario.PENDENTE)
        self.assertEqual(versao.avaliacao.didatica, 4)

    def test_dados_sensiveis_e_retirada(self):
        self.ativar()
        self.moderador()
        versao = self.versao()
        versao.texto = "meu email é contato@exemplo.com"
        self.db.commit()
        with patch.object(openai_triagem, "classificar") as chamada:
            self.assertEqual(self.triagem(versao)[1]["status"], "DADOS_SENSIVEIS")
            versao.estado = EstadoComentario.RETIRADO
            self.db.commit()
            self.assertEqual(self.triagem(versao)[0], 409)
            chamada.assert_not_called()

    def test_indisponibilidade(self):
        self.ativar()
        self.moderador()
        versao = self.versao()
        with patch.object(
            openai_triagem, "classificar", side_effect=openai_triagem.TriagemIndisponivel()
        ):
            self.assertEqual(self.triagem(versao)[1]["status"], "INDISPONIVEL")
        self.db.expire_all()
        self.assertEqual(versao.estado, EstadoComentario.PENDENTE)

    def test_mudanca_durante_analise(self):
        self.ativar()
        self.moderador()
        versao = self.versao()

        def mudou(*args, **kwargs):
            versao.estado = EstadoComentario.RETIRADO
            self.db.commit()
            return ClassificacaoIA(categorias=[], sinalizado=False, modelo="omni-moderation-latest")

        with patch.object(openai_triagem, "classificar", side_effect=mudou):
            self.assertEqual(self.triagem(versao)[0], 409)
