from typing import Literal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Categoria = Literal[
    "DADO_INCORRETO",
    "COMENTARIO_ILICITO",
    "NOTA_SUSPEITA",
    "FRAUDE_COORDENADA",
    "EXPOSICAO_PESSOAL",
    "DIREITO_LGPD",
    "OUTRA",
]


class CriarSolicitacao(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    categoria: Categoria
    alvo: str = Field(min_length=1, max_length=1000)
    descricao: str = Field(min_length=10, max_length=4000)
    evidencia: str = Field(min_length=1, max_length=4000)


class ConsultarSolicitacao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    protocolo: UUID
    chave: str = Field(min_length=32, max_length=100)


class ComplementarSolicitacao(ConsultarSolicitacao):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    texto: str = Field(min_length=1, max_length=4000)


class AtenderSolicitacao(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    tipo: Literal["TRIAGEM", "PROVIDENCIA", "RESPOSTA"]
    texto: str = Field(min_length=1, max_length=4000)


class ReciboSolicitacao(BaseModel):
    protocolo: UUID
    chave: str
    recebido_em: datetime


class EventoPublico(BaseModel):
    tipo: Literal["RESPOSTA", "COMPLEMENTO"]
    texto: str
    data: datetime


class EventoInterno(BaseModel):
    tipo: Literal["TRIAGEM", "PROVIDENCIA", "RESPOSTA", "COMPLEMENTO"]
    texto: str
    data: datetime
    responsavel_id: UUID | None


class ResumoSolicitacao(BaseModel):
    protocolo: UUID
    categoria: Categoria
    recebido_em: datetime


class ConsultaPublica(ResumoSolicitacao):
    alvo: str
    descricao: str
    evidencia: str
    historico: list[EventoPublico]


class ConsultaInterna(ResumoSolicitacao):
    alvo: str
    descricao: str
    evidencia: str
    historico: list[EventoInterno]


class Disponibilidade(BaseModel):
    ativo: bool


class Permissao(BaseModel):
    responder: bool
