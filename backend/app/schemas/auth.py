import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


EMAIL_INSTITUCIONAL = re.compile(r"^[^@\s]+@aluno\.unb\.br$", re.IGNORECASE)


class CadastroRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str
    email: str = Field(max_length=150)
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome: str) -> str:
        nome_normalizado = nome.strip()
        if not nome_normalizado:
            raise ValueError("nome não pode ser vazio")
        if len(nome_normalizado) > 100:
            raise ValueError("nome deve ter no máximo 100 caracteres")
        return nome_normalizado

    @field_validator("email")
    @classmethod
    def validar_email(cls, email: str) -> str:
        email_normalizado = email.strip().casefold()
        if not EMAIL_INSTITUCIONAL.fullmatch(email_normalizado):
            raise ValueError("email deve pertencer ao domínio @aluno.unb.br")
        return email_normalizado


class ConfirmacaoEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=32, max_length=200)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1, max_length=150)
    senha: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, email: str) -> str:
        return email.strip().casefold()


class SessaoResponse(BaseModel):
    autenticado: bool


class MensagemResponse(BaseModel):
    message: str
