import re
from urllib.parse import parse_qsl

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from app.domain.termos import TERMOS_VERSAO


EMAIL_INSTITUCIONAL = re.compile(r"^[^@\s]+@aluno\.unb\.br$", re.IGNORECASE)
UUID_CANONICO = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
RETORNO_AVALIACAO = re.compile(
    rf"/professores/{UUID_CANONICO}/disciplinas/{UUID_CANONICO}/avaliar", re.IGNORECASE
)


class CadastroRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str
    email: str = Field(max_length=150)
    senha: str = Field(min_length=8, max_length=128)
    ciencia_termos: StrictBool
    termos_versao: str = Field(max_length=32)

    @field_validator("ciencia_termos")
    @classmethod
    def validar_ciencia_termos(cls, valor: bool) -> bool:
        if valor is not True:
            raise ValueError("Confirme a ciência dos Termos de Uso para criar a conta.")
        return valor

    @field_validator("termos_versao")
    @classmethod
    def validar_versao_termos(cls, valor: str) -> str:
        if valor != TERMOS_VERSAO:
            raise ValueError("Reabra os Termos de Uso e confirme a versão vigente.")
        return valor

    return_to: str | None = Field(default=None, max_length=2048)

    @field_validator("return_to")
    @classmethod
    def validar_retorno(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        caminho, separador, query = valor.partition("?")
        invalido = (
            not RETORNO_AVALIACAO.fullmatch(caminho)
            or "#" in valor
            or re.search(r"[\x00-\x1f\x7f]|%(?![\da-fA-F]{2})", valor)
        )
        if separador and not invalido:
            pares = parse_qsl(query, keep_blank_values=True)
            parametros = dict(pares)
            invalido = (
                len(pares) != 3
                or set(parametros) != {"busca", "q", "ordem"}
                or parametros.get("busca") not in {"professores", "disciplinas"}
                or parametros.get("ordem") not in {"nome", "unidade"}
                or re.search(r"[\x00-\x1f\x7f]", parametros.get("q", ""))
            )
        if invalido:
            raise ValueError(
                "return_to deve ser uma rota interna de avaliação com UUIDs válidos e contexto de busca permitido"
            )
        return valor

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


class RecuperarSenhaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1, max_length=150)

    @field_validator("email")
    @classmethod
    def validar_email(cls, email: str) -> str:
        return CadastroRequest.validar_email(email)


class RedefinirSenhaRequest(ConfirmacaoEmailRequest):
    senha: str = Field(min_length=8, max_length=128)
