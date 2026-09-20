import logging
from typing import Protocol

import resend

from app.core.config import EMAIL_BACKEND, EMAIL_FROM, RESEND_API_KEY


logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    pass


class EmailSender(Protocol):
    def enviar_confirmacao(self, destinatario: str, link: str) -> None: ...


class ConsoleEmailSender:
    def enviar_confirmacao(self, destinatario: str, link: str) -> None:
        logger.warning(
            "EMAIL_BACKEND=console: confirmacao para %s: %s",
            destinatario,
            link,
        )


class ResendEmailSender:
    def __init__(self, api_key: str, remetente: str) -> None:
        if not api_key:
            raise EmailDeliveryError("RESEND_API_KEY não configurada")
        self.api_key = api_key
        self.remetente = remetente

    def enviar_confirmacao(self, destinatario: str, link: str) -> None:
        try:
            resend.api_key = self.api_key
            resend.Emails.send(
                {
                    "from": self.remetente,
                    "to": [destinatario],
                    "subject": "Confirme seu e-mail institucional no UnDb",
                    "html": (
                        "<p>Confirme seu e-mail institucional para poder avaliar "
                        "professores e disciplinas no UnDb.</p>"
                        f'<p><a href="{link}">Confirmar e-mail</a></p>'
                        "<p>Este link expira em 24 horas.</p>"
                    ),
                }
            )
        except Exception as erro:
            raise EmailDeliveryError("falha ao enviar e-mail de confirmação") from erro


def get_email_sender() -> EmailSender:
    if EMAIL_BACKEND == "console":
        return ConsoleEmailSender()
    if EMAIL_BACKEND == "resend":
        return ResendEmailSender(RESEND_API_KEY, EMAIL_FROM)
    raise EmailDeliveryError(f"EMAIL_BACKEND desconhecido: {EMAIL_BACKEND}")
