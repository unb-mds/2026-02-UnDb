"""#266/bloco 2: HTTP, dados e contadores no PostgreSQL descartável migrado."""

import os
import secrets
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core import config
from app.core.dependencia_limite_abuso import obter_limitador
from app.core.limite_abuso import IdentidadeAbuso, TipoIdentidade, derivar_chave
from app.main import app
from app.models.contador_abuso import ContadorAbuso
from app.models.sessao_usuario import SessaoUsuario
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.models.usuario import Usuario
from app.services import auth_service
from app.services.limite_abuso_service import LimitadorAbuso
from tests.auth_http_fixtures import AuthHttpFixture
from tests.test_limite_abuso_postgres import engine_ensaio


@unittest.skipUnless(
    os.environ.get("ABUSO_POSTGRES_TEST_URL"), "Exige PostgreSQL descartável migrado."
)
class AuthAbusoPostgresTest(AuthHttpFixture, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = make_url(os.environ["ABUSO_POSTGRES_TEST_URL"])
        if (
            url.drivername != "postgresql+psycopg2"
            or url.host not in {"localhost", "127.0.0.1", "::1"}
            or url.database not in {"undb_266_test", "ci"}
        ):
            raise ValueError("Somente banco descartável local undb_266_test ou CI ci.")
        cls.pg_engine = engine_ensaio(url, pool_size=5)

    @classmethod
    def tearDownClass(cls):
        cls.pg_engine.dispose()

    def setUp(self):
        self.agora = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        self.secret = secrets.token_urlsafe(32)
        self.secret_patch = patch.object(config, "ABUSO_HMAC_SECRET", self.secret)
        self.politicas = {}
        self.politicas_patch = patch.object(config, "ABUSO_POLITICAS", self.politicas)
        self.secret_patch.start()
        self.politicas_patch.start()
        self.limitador = LimitadorAbuso(lambda: Session(self.pg_engine), lambda db: self.agora)
        self.iniciar_http(self.pg_engine, self.limitador)
        self.email = self.novo_email()

    def tearDown(self):
        self.encerrar_http()
        self.secret_patch.stop()
        self.politicas_patch.stop()
        with Session(self.pg_engine) as db, db.begin():
            ids = select(Usuario.id).where(Usuario.email.like("auth266.%@aluno.unb.br"))
            for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
                db.execute(delete(modelo).where(modelo.usuario_id.in_(ids)))
            db.execute(delete(Usuario).where(Usuario.id.in_(ids)))
            db.execute(delete(ContadorAbuso).where(ContadorAbuso.operacao.like("auth.%")))

    def novo_email(self):
        return f"auth266.{uuid4().hex}@aluno.unb.br"

    def cadastro(self, email=None):
        return self.post(
            "cadastro",
            {"nome": "Pessoa sintética", "email": email or self.email, "senha": self.senha},
        )

    def test_intervalo_compartilhado_nega_reenvio_e_recuperacao_sem_efeitos(self):
        self.assertEqual(self.cadastro().status_code, 202)
        for rota in ("reenviar-confirmacao", "recuperar-senha"):
            r = self.post(rota, {"email": self.email.upper()})
            self.assertEqual(r.status_code, 429)
            self.assertEqual(r.headers["retry-after"], str(config.AUTH_EMAIL_INTERVALO_SEGUNDOS))
        self.assertEqual(len(self.sender.envios), 1)
        self.assertEqual(self.contar(TokenConfirmacaoEmail), 1)
        self.assertEqual(self.contar(TokenRecuperacaoSenha), 0)

    def test_reenvio_apos_intervalo_preserva_link_anterior(self):
        self.cadastro()
        anterior = self.sender.token()
        self.agora += timedelta(seconds=config.AUTH_EMAIL_INTERVALO_SEGUNDOS)
        self.assertEqual(self.post("reenviar-confirmacao", {"email": self.email}).status_code, 202)
        self.assertEqual(len(self.sender.envios), 2)
        self.assertEqual(self.post("confirmar", {"token": anterior}).status_code, 200)
        self.assertEqual(self.post("confirmar", {"token": anterior}).status_code, 400)

    def test_orcamento_diario_compartilhado_inclui_destino_inexistente(self):
        self.politicas["auth.email_dia"] = {"quantidade_global": 2}
        self.assertEqual(self.cadastro().status_code, 202)
        self.assertEqual(
            self.post("recuperar-senha", {"email": self.novo_email()}).status_code, 202
        )
        self.agora += timedelta(seconds=config.AUTH_EMAIL_INTERVALO_SEGUNDOS)
        r = self.post("reenviar-confirmacao", {"email": self.email})
        self.assertEqual(r.status_code, 429)
        self.assertEqual(len(self.sender.envios), 1)
        self.assertEqual(self.contar(TokenConfirmacaoEmail), 1)

    def test_orcamento_de_envio_reseta_no_dia_utc_e_nao_apos_24h_do_primeiro(self):
        self.politicas["auth.email_dia"] = {"quantidade_global": 2}
        self.agora = self.agora.replace(hour=23, minute=59, second=59)
        self.assertEqual(self.cadastro(self.novo_email()).status_code, 202)
        self.assertEqual(self.cadastro(self.novo_email()).status_code, 202)
        self.assertEqual(self.cadastro(self.novo_email()).status_code, 429)
        self.agora += timedelta(seconds=1)
        self.assertEqual(self.cadastro(self.novo_email()).status_code, 202)
        self.assertEqual(self.cadastro(self.novo_email()).status_code, 202)
        self.assertEqual(self.cadastro(self.novo_email()).status_code, 429)
        self.assertEqual(len(self.sender.envios), 4)
        self.assertEqual(self.contar(Usuario), 4)

    def test_login_100_tentativas_sem_lockout_e_retomada_apos_janela(self):
        self.usuario()
        self.politicas["auth.login"] = {
            "quantidade_global": 1000,
            "atraso_inicial_segundos": 0,
            "atraso_maximo_segundos": 0,
        }
        senha_errada = secrets.token_urlsafe(24)
        for _ in range(config.AUTH_LOGIN_MAX_TENTATIVAS):
            self.assertEqual(
                self.post("login", {"email": self.email, "senha": senha_errada}).status_code, 401
            )
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": self.senha}).status_code, 429
        )
        self.assertEqual(self.contar(SessaoUsuario), 0)
        self.agora += timedelta(seconds=config.AUTH_LOGIN_JANELA_SEGUNDOS)
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": self.senha}).status_code, 200
        )

    def test_atraso_progressivo_e_sucesso_reinicia_so_identidade(self):
        self.usuario()
        self.politicas["auth.login"] = {
            "atraso_apos": 1,
            "atraso_inicial_segundos": 1,
            "atraso_maximo_segundos": 2,
        }
        errada = secrets.token_urlsafe(24)
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": errada}).status_code, 401
        )
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": self.senha}).status_code, 429
        )
        self.agora += timedelta(seconds=1)
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": self.senha}).status_code, 200
        )
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": errada}).status_code, 401
        )
        identidade = IdentidadeAbuso(TipoIdentidade.EMAIL, self.email)
        with Session(self.engine) as db:
            individual = db.get(
                ContadorAbuso, ("auth.login", derivar_chave(self.secret, "auth.login", identidade))
            )
            global_ = db.get(
                ContadorAbuso, ("auth.login", derivar_chave(self.secret, "auth.login", None))
            )
            self.assertEqual(individual.quantidade, 1)
            self.assertEqual(global_.quantidade, 4)

    def test_moderador_nao_ignora_login_e_normalizacao_tem_mesma_restricao(self):
        self.usuario(moderador=True)
        self.politicas["auth.login"] = {
            "quantidade": 1,
            "atraso_inicial_segundos": 0,
            "atraso_maximo_segundos": 0,
        }
        errada = secrets.token_urlsafe(24)
        conhecida = self.post("login", {"email": self.email, "senha": errada})
        conhecida_negada = self.post(
            "login", {"email": " " + self.email.upper() + " ", "senha": self.senha}
        )
        email_ausente = self.novo_email()
        desconhecida = self.post("login", {"email": email_ausente, "senha": errada})
        desconhecida_negada = self.post(
            "login", {"email": email_ausente.upper(), "senha": self.senha}
        )
        self.assertEqual(conhecida.status_code, 401)
        self.assertEqual(conhecida_negada.status_code, 429)
        self.assertEqual(desconhecida.status_code, 401)
        self.assertEqual(desconhecida.json(), conhecida.json())
        self.assertEqual(desconhecida_negada.status_code, 429)
        self.assertEqual(desconhecida_negada.json(), conhecida_negada.json())

    def test_observe_mede_sem_bloquear_o_login(self):
        self.usuario()
        self.politicas["auth.login"] = {
            "quantidade": 1,
            "modo": "observe",
            "atraso_inicial_segundos": 0,
            "atraso_maximo_segundos": 0,
        }
        errada = secrets.token_urlsafe(24)
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": errada}).status_code, 401
        )
        with self.assertLogs("app.services.limite_abuso_service", level="WARNING") as logs:
            self.assertEqual(
                self.post("login", {"email": self.email, "senha": errada}).status_code, 401
            )
        self.assertIn("abuso.observado", str(logs.output))
        self.assertNotIn(self.email, str(logs.output))

    def test_troca_de_tokens_nao_contorna_global_confirmacao_ou_redefinicao(self):
        for operacao, rota in (
            ("auth.confirmacao", "confirmar"),
            ("auth.redefinicao", "redefinir-senha"),
        ):
            self.politicas[operacao] = {"quantidade_global": 2}
            for status in (400, 400, 429):
                corpo = {"token": secrets.token_urlsafe(32)}
                if rota == "redefinir-senha":
                    corpo["senha"] = self.senha
                self.assertEqual(self.post(rota, corpo).status_code, status)
        self.assertEqual(self.contar(SessaoUsuario), 0)

    def test_timeout_real_do_limitador_nao_chega_a_autenticar(self):
        self.post("login", {"email": self.email, "senha": self.senha})
        chave = derivar_chave(self.secret, "auth.login", None)
        with Session(self.engine) as bloqueio, bloqueio.begin():
            bloqueio.execute(
                select(ContadorAbuso)
                .where(ContadorAbuso.operacao == "auth.login", ContadorAbuso.chave == chave)
                .with_for_update()
            )
            with patch.object(auth_service, "autenticar") as autenticar:
                r = self.post("login", {"email": self.novo_email(), "senha": self.senha})
            self.assertEqual(r.status_code, 503)
            self.assertIn("retry-after", r.headers)
            autenticar.assert_not_called()

    def test_jornada_confirmacao_recuperacao_uso_unico_revogacao_e_logout(self):
        self.assertEqual(self.cadastro().status_code, 202)
        confirmacao = self.sender.token()
        self.assertEqual(self.post("confirmar", {"token": confirmacao}).status_code, 200)
        self.assertEqual(
            self.post("login", {"email": self.email, "senha": self.senha}).status_code, 200
        )
        self.agora += timedelta(seconds=config.AUTH_EMAIL_INTERVALO_SEGUNDOS)
        self.assertEqual(self.post("recuperar-senha", {"email": self.email}).status_code, 202)
        primeiro = self.sender.token()
        self.assertEqual(self.post("recuperar-senha", {"email": self.email}).status_code, 429)
        self.agora += timedelta(seconds=config.AUTH_EMAIL_INTERVALO_SEGUNDOS)
        self.assertEqual(self.post("recuperar-senha", {"email": self.email}).status_code, 202)
        segundo = self.sender.token()
        nova = secrets.token_urlsafe(24)
        self.assertEqual(
            self.post("redefinir-senha", {"token": primeiro, "senha": nova}).status_code, 200
        )
        self.assertEqual(self.contar(SessaoUsuario), 0)
        for token in (primeiro, segundo):
            self.assertEqual(
                self.post("redefinir-senha", {"token": token, "senha": nova}).status_code, 400
            )
        self.assertFalse(self.client.get("/api/auth/sessao").json()["autenticado"])
        self.assertEqual(self.post("login", {"email": self.email, "senha": nova}).status_code, 200)
        self.assertEqual(self.post("logout", None).status_code, 200)

    def test_sessao_valida_e_logout_funcionam_com_limitador_indisponivel(self):
        self.usuario()
        self.post("login", {"email": self.email, "senha": self.senha})
        fabrica = Mock(side_effect=RuntimeError("falha sintética"))
        app.dependency_overrides[obter_limitador] = lambda: LimitadorAbuso(fabrica)
        self.assertTrue(self.client.get("/api/auth/sessao").json()["autenticado"])
        self.assertEqual(self.post("logout", None).status_code, 200)
        fabrica.assert_not_called()
