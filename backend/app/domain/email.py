"""Normalização compartilhável, sem validação de existência ou acesso ao banco."""


def normalizar_email(valor: str) -> str:
    # Mesma regra dos contratos atuais; não remover pontos ou aliases do endereço.
    return valor.strip().casefold()
