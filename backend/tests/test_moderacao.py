"""RF20/RF22 HTTP flows, using the existing comment integration fixture."""

import asyncio
import unittest
from unittest.mock import patch
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
    _criar_avaliacao_com_comentario = (
        comentarios.ComentarioHttpIntegrationTest._criar_avaliacao_com_comentario
    )
    _obter_comentario = comentarios.ComentarioHttpIntegrationTest._obter_comentario

    def moderador(self):
        usuario = Usuario(
            nome="Moderador",
            email="mod@aluno.unb.br",
            password_hash="teste",
            email_confirmado=True,
            moderador=True,
        )
        self.db.add(usuario)
        self.db.flush()
        self.db.add(
            SessaoUsuario(
                usuario_id=usuario.id,
                token_hash=gerar_hash_token("mod"),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            )
        )
        self.db.commit()
        return usuario

    def versao(self, estado=EstadoComentario.PENDENTE, usuario=None):
        avaliacao = self._criar_avaliacao_com_comentario(usuario or self.usuario, "texto", estado)
        return self._obter_comentario(avaliacao.id)

    def acao(self, versao_id, acao, token="mod", motivo="revisao humana"):
        return asyncio.run(
            self._request(
                "POST",
                f"/api/moderacao/comentarios/{versao_id}/acoes",
                {"acao": acao, "motivo": motivo},
                token,
            )
        )

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
        code, resultado = asyncio.run(
            self._request("GET", "/api/comentarios/meu", token=self.token)
        )
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

    def test_aprovacao_inicial_nao_consulta_denuncias(self):
        self.moderador()
        versao = self.versao()
        with (
            patch(
                "app.repositories.denuncia_repository.listar",
                side_effect=AssertionError("dependencia indevida"),
            ),
            patch(
                "app.repositories.denuncia_repository.existe_da_conta",
                side_effect=AssertionError("dependencia indevida"),
            ),
        ):
            self.assertEqual(self.acao(versao.id, "APROVAR")[0], 200)

    def test_estados_finais_nao_podem_ser_restaurados_e_schema_exige_motivo(self):
        self.moderador()
        versao = self.versao()
        for estado in (
            EstadoComentario.RETIRADO,
            EstadoComentario.REMOVIDO,
            EstadoComentario.REJEITADO,
            EstadoComentario.SUBSTITUIDO,
        ):
            versao.estado = estado
            versao.texto = None
            self.db.commit()
            for acao in ("APROVAR", "REJEITAR", "MANTER", "RESTAURAR", "REMOVER"):
                with self.subTest(estado=estado, acao=acao):
                    self.assertEqual(self.acao(versao.id, acao)[0], 409)
        code, _ = asyncio.run(
            self._request(
                "POST", f"/api/moderacao/comentarios/{versao.id}/acoes", {"acao": "REMOVER"}, "mod"
            )
        )
        self.assertEqual(code, 422)

    def test_fila_privada_e_filtro(self):
        self.moderador()
        self.versao()
        self.assertEqual(asyncio.run(self._request("GET", "/api/moderacao/comentarios"))[0], 401)
        code, fila = asyncio.run(self._request("GET", "/api/moderacao/comentarios", token="mod"))
        self.assertEqual(code, 200)
        self.assertEqual(fila[0]["autor"]["email"], self.usuario.email)
        self.assertEqual(
            asyncio.run(
                self._request("GET", "/api/moderacao/comentarios?estado=SUSPENSO", token="mod")
            )[1],
            [],
        )

    def test_revogacao_imediata_e_conta_nao_confirmada(self):
        from app.repositories.moderacao_repository import definir_papel

        usuario = self.moderador()
        definir_papel(self.db, usuario.email, False)
        self.db.commit()
        self.assertEqual(
            asyncio.run(self._request("GET", "/api/moderacao/comentarios", token="mod"))[0], 403
        )
        with self.assertRaises(ValueError):
            definir_papel(self.db, self.usuario_nao_confirmado.email, True)

    def test_descarte_sete_dias_preserva_pendentes_suspensos_e_mensagens(self):
        from app.repositories.moderacao_repository import descartar_vencidos
        from app.models.denuncia import Agradecimento

        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        from app.repositories import denuncia_repository
        from app.models.enums import MotivoDenuncia

        inicio = datetime.now(timezone.utc)
        denuncia_repository.criar(
            self.db, versao.id, self.usuario_nao_confirmado.id, MotivoDenuncia.SPAM, inicio
        )
        self.db.commit()
        with patch("app.services.moderacao_service.agora_utc", return_value=inicio):
            self.assertEqual(self.acao(versao.id, "REMOVER")[0], 200)
        self.db.refresh(versao)
        decisao = self.db.scalar(select(DecisaoModeracao))
        pendente = self.versao(usuario=self.outro_usuario)
        from app.models.comentario_versao import ComentarioVersao

        suspenso = ComentarioVersao(
            avaliacao_id=pendente.avaliacao_id,
            texto="texto suspenso",
            estado=EstadoComentario.SUSPENSO,
        )
        self.db.add(suspenso)
        self.db.commit()
        descartar_vencidos(self.db, inicio + timedelta(days=7) - timedelta(microseconds=1))
        self.assertEqual(versao.texto, "texto")
        self.assertIsNotNone(self.db.get(DecisaoModeracao, decisao.id))
        self.db.commit()
        with patch(
            "app.services.comentario_service.agora_utc", return_value=inicio + timedelta(days=7)
        ):
            code, comentarios_autor = asyncio.run(
                self._request("GET", "/api/comentarios/meu", token=self.token)
            )
        self.assertEqual(code, 200)
        self.assertIsNone(comentarios_autor[0]["texto"])
        self.db.expire_all()
        self.assertIsNone(versao.texto)
        self.assertIsNone(self.db.scalar(select(DecisaoModeracao)))
        self.assertEqual(pendente.texto, "texto")
        self.assertEqual(suspenso.texto, "texto suspenso")
        self.assertIsNotNone(self.db.scalar(select(Agradecimento)))

    def test_transacao_reverte_acao_e_encerramento_em_falha(self):
        from app.repositories import denuncia_repository
        from app.models.enums import MotivoDenuncia

        self.moderador()
        versao = self.versao(EstadoComentario.PUBLICADO)
        denuncia_repository.criar(
            self.db,
            versao.id,
            self.usuario_nao_confirmado.id,
            MotivoDenuncia.SPAM,
            datetime.now(timezone.utc),
        )
        self.db.commit()
        with patch(
            "app.repositories.moderacao_repository.registrar_decisao",
            side_effect=RuntimeError("falha simulada"),
        ):
            with self.assertRaises(RuntimeError):
                self.acao(versao.id, "REMOVER")
        self.db.refresh(versao)
        self.assertEqual(versao.estado, EstadoComentario.PUBLICADO)
        self.assertEqual(denuncia_repository.contar_contas(self.db, versao.id), 1)
        self.assertEqual(
            denuncia_repository.listar_agradecimentos(self.db, self.usuario_nao_confirmado.id), []
        )


if __name__ == "__main__":
    unittest.main()
