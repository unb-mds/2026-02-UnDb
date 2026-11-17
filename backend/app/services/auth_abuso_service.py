"""Políticas de autenticação do #266/bloco 2, sem chaves por IP ou bypass por papel."""

from datetime import timedelta

from app.core import config
from app.core.dependencia_limite_abuso import AbusoExcedido, LimitadorIndisponivel
from app.core.limite_abuso import IdentidadeAbuso, TipoIdentidade
from app.domain.limite_abuso import FalhaLimite, PoliticaAbuso, ResultadoLimite
from app.services.limite_abuso_service import LimitadorAbuso


def politica_auth(operacao: str) -> PoliticaAbuso:
    quantidade = config.AUTH_EMAIL_MAX_TENTATIVAS
    janela = config.AUTH_EMAIL_JANELA_SEGUNDOS
    global_ = config.AUTH_ABUSO_GLOBAL_MINUTO
    global_janela = config.AUTH_ABUSO_MINUTO_SEGUNDOS
    campos = {}
    if operacao == "auth.login":
        quantidade = config.AUTH_LOGIN_MAX_TENTATIVAS
        janela = config.AUTH_LOGIN_JANELA_SEGUNDOS
        campos = {
            "atraso_apos": config.AUTH_LOGIN_ATRASO_APOS,
            "atraso_inicial_segundos": config.AUTH_LOGIN_ATRASO_INICIAL_SEGUNDOS,
            "atraso_maximo_segundos": config.AUTH_LOGIN_ATRASO_MAX_SEGUNDOS,
        }
    elif operacao in {"auth.confirmacao", "auth.redefinicao"}:
        quantidade = config.AUTH_TOKEN_MAX_TENTATIVAS
        janela = config.AUTH_TOKEN_JANELA_SEGUNDOS
        if operacao == "auth.redefinicao":
            global_ = config.AUTH_REDEFINICAO_GLOBAL_MINUTO
    elif operacao == "auth.email_destino":
        quantidade = config.AUTH_EMAIL_DESTINO_MAX
        janela = config.AUTH_EMAIL_INTERVALO_SEGUNDOS
    elif operacao == "auth.email_dia":
        quantidade = global_ = config.AUTH_EMAIL_ORCAMENTO_DIARIO
        janela = global_janela = config.AUTH_EMAIL_DIA_SEGUNDOS
        campos = {"alinhar_janela_utc": True}
    elif operacao not in {"auth.cadastro", "auth.reenvio", "auth.recuperacao"}:
        raise ValueError("Operação de autenticação não registrada.")
    dados = {
        "quantidade": quantidade,
        "janela_segundos": janela,
        "quantidade_global": global_,
        "janela_global_segundos": global_janela,
        "modo": config.AUTH_ABUSO_MODO,
        "falha": FalhaLimite.FECHAR,
        **campos,
        **config.ABUSO_POLITICAS.get(operacao, {}),
    }
    politica = PoliticaAbuso(operacao=operacao, **dados)
    if politica.falha != FalhaLimite.FECHAR:
        raise ValueError("Autenticação não pode continuar na falha do limitador.")
    if operacao == "auth.login" and politica.quantidade > config.AUTH_LOGIN_MAX_TENTATIVAS:
        raise ValueError("Política supera o teto de tentativas de login configurado.")
    if operacao == "auth.email_dia" and (
        not 0 < politica.quantidade_global < config.AUTH_EMAIL_COTA_DIARIA_PROVEDOR
        or politica.quantidade_global > config.AUTH_EMAIL_ORCAMENTO_DIARIO
        or not politica.alinhar_janela_utc
        or politica.janela_global_segundos != timedelta(days=1).total_seconds()
    ):
        raise ValueError("Orçamento diário incompatível com a cota configurada.")
    return politica


class ProtecaoAuth:
    def __init__(self, limitador: LimitadorAbuso):
        self.limitador = limitador

    def _politica(self, operacao: str) -> PoliticaAbuso:
        try:
            return politica_auth(operacao)
        except (ValueError, TypeError, KeyError):
            resultado = self.limitador.falha()
            raise LimitadorIndisponivel(resultado.retry_after) from None

    def exigir(self, operacao: str, identidade: IdentidadeAbuso | None = None) -> ResultadoLimite:
        resultado = self.limitador.consumir(self._politica(operacao), identidade)
        if not resultado.permitido:
            erro = LimitadorIndisponivel if resultado.indisponivel else AbusoExcedido
            raise erro(resultado.retry_after)
        return resultado

    def email(self, operacao: str, email: str):
        identidade = IdentidadeAbuso(TipoIdentidade.EMAIL, email)
        # Também para endereço inexistente/confirmado: orçamento e resposta não revelam conta.
        self.exigir(operacao, identidade)
        self.exigir("auth.email_destino", identidade)
        self.exigir("auth.email_dia")

    def login(self, email: str):
        self.exigir("auth.login", IdentidadeAbuso(TipoIdentidade.EMAIL, email))

    def token(self, operacao: str, token: str):
        self.exigir(operacao, IdentidadeAbuso(TipoIdentidade.TOKEN, token))

    def sucesso_login(self, email: str):
        politica = self._politica("auth.login")
        if not self.limitador.reiniciar_identidade(
            politica, IdentidadeAbuso(TipoIdentidade.EMAIL, email)
        ):
            resultado = self.limitador.falha()
            raise LimitadorIndisponivel(resultado.retry_after)
