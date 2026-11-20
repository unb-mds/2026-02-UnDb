"""Um voto por conta e versão; sem histórico ou identidade pública."""

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VotoComentario(Base):
    __tablename__ = "votos_comentario"

    comentario_versao_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("comentario_versoes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    usuario_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    voto: Mapped[str] = mapped_column(String(8), nullable=False)

    __table_args__ = (
        CheckConstraint("voto IN ('UTIL', 'NAO_UTIL')", name="ck_voto_comentario_valor"),
    )
