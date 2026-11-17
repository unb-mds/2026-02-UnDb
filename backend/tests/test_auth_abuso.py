"""#266 bloco 2: políticas e contratos HTTP de abuso em autenticação."""

import os
import secrets
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", secrets.token_urlsafe(32))

from app.core import config
from app.core.dependencia_limite_abuso import AbusoExcedido, LimitadorIndisponivel
from app.domain.limite_abuso import MotivoLimite, ResultadoLimite
from app.services.auth_abuso_service import ProtecaoAuth, politica_auth


class PoliticasAuthTest(unittest.TestCase):
    def setUp(self):
        self.overrides = patch.object(config, "ABUSO_POLITICAS", {})
        self.overrides.start()

    def tearDown(self):
        self.overrides.stop()

    def test_perfis_com_orcamento_global_fechados_e_configuraveis(self):
        for operacao in (
            "auth.cadastro",
            "auth.login",
            "auth.confirmacao",
            "auth.reenvio",
            "auth.recuperacao",
            "auth.redefinicao",
            "auth.email_destino",
            "auth.email_dia",
        ):
            p = politica_auth(operacao)
            self.assertGreater(p.quantidade_global, 0)
            self.assertEqual(p.modo, "enforce")
            self.assertEqual(p.falha, "fechar")
        diario = politica_auth("auth.email_dia")
        self.assertLess(diario.quantidade_global, config.AUTH_EMAIL_COTA_DIARIA_PROVEDOR)
        self.assertTrue(diario.alinhar_janela_utc)
        with patch.object(
            config, "ABUSO_POLITICAS", {"auth.login": {"modo": "observe", "quantidade": 2}}
        ):
            self.assertEqual(politica_auth("auth.login").modo, "observe")
            self.assertEqual(politica_auth("auth.login").quantidade, 2)

    def test_cota_invalida_ou_override_inseguro_fecha(self):
        for override in (
            {"quantidade_global": config.AUTH_EMAIL_COTA_DIARIA_PROVEDOR},
            {"alinhar_janela_utc": False},
            {"janela_global_segundos": 60},
            {"falha": "seguir"},
        ):
            with (
                patch.object(config, "ABUSO_POLITICAS", {"auth.email_dia": override}),
                self.assertRaises(ValueError),
            ):
                politica_auth("auth.email_dia")
        with (
            patch.object(config, "AUTH_EMAIL_ORCAMENTO_DIARIO", 100),
            self.assertRaises(ValueError),
        ):
            politica_auth("auth.email_dia")

    def test_identidade_e_cota_compartilhadas_antes_de_consultar_conta(self):
        limitador = Mock()
        limitador.consumir.return_value = ResultadoLimite(True, 0, MotivoLimite.PERMITIDO)
        ProtecaoAuth(limitador).email("auth.cadastro", " PESSOA@ALUNO.UNB.BR ")
        chamadas = limitador.consumir.call_args_list
        self.assertEqual(
            [chamada.args[0].operacao for chamada in chamadas],
            ["auth.cadastro", "auth.email_destino", "auth.email_dia"],
        )
        self.assertEqual(chamadas[0].args[1], chamadas[1].args[1])
        self.assertIsNone(chamadas[2].args[1])

    def test_falha_503_excesso_429_e_reset_individual(self):
        limitador = Mock()
        limitador.falha.return_value = ResultadoLimite(
            False, 5, MotivoLimite.INDISPONIVEL, indisponivel=True
        )
        guard = ProtecaoAuth(limitador)
        for indisponivel, erro in ((False, AbusoExcedido), (True, LimitadorIndisponivel)):
            limitador.consumir.return_value = ResultadoLimite(
                False, 7, MotivoLimite.GLOBAL, indisponivel=indisponivel
            )
            with self.assertRaises(erro):
                guard.login("pessoa@aluno.unb.br")
        limitador.reiniciar_identidade.return_value = True
        guard.sucesso_login("pessoa@aluno.unb.br")
        self.assertEqual(limitador.reiniciar_identidade.call_args.args[0].operacao, "auth.login")
        limitador.reiniciar_identidade.return_value = False
        with self.assertRaises(LimitadorIndisponivel):
            guard.sucesso_login("pessoa@aluno.unb.br")
