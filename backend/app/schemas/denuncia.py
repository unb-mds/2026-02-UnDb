from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import MotivoDenuncia
from app.schemas.moderacao import IdentidadeInterna


class DenunciaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    motivo: MotivoDenuncia


class ConfirmacaoDenuncia(BaseModel):
    mensagem: str = "Denuncia registrada. Obrigado por contribuir."


class DenunciaInterna(BaseModel):
    id: UUID
    comentario_versao_id: UUID
    motivo: MotivoDenuncia
    estado: Literal["EM_ABERTO"] = "EM_ABERTO"
    created_at: datetime
    denunciante: IdentidadeInterna | None


class DenunciasDaVersao(BaseModel):
    autenticadas: list[DenunciaInterna]
    visitantes: list[DenunciaInterna]
    contas_distintas: int
    total_visitantes: int


class AgradecimentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    mensagem: str = "Obrigado por contribuir com a moderacao do conteudo."
