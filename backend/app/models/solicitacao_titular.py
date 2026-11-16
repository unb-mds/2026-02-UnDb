from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SolicitacaoTitular(Base):
    __tablename__ = "solicitacoes_titulares"
    __table_args__ = (
        CheckConstraint(
            "categoria IN ('DADO_INCORRETO', 'COMENTARIO_ILICITO', 'NOTA_SUSPEITA', 'FRAUDE_COORDENADA', 'EXPOSICAO_PESSOAL', 'DIREITO_LGPD', 'OUTRA')",
            name="ck_solicitacao_categoria",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    chave_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    categoria: Mapped[str] = mapped_column(String(40), nullable=False)
    alvo: Mapped[str] = mapped_column(String(1000), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    evidencia: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )


class EventoSolicitacao(Base):
    __tablename__ = "eventos_solicitacoes"
    __table_args__ = (
        CheckConstraint(
            "(tipo = 'COMPLEMENTO' AND autor_id IS NULL) OR (tipo IN ('TRIAGEM', 'PROVIDENCIA', 'RESPOSTA') AND autor_id IS NOT NULL)",
            name="ck_evento_tipo_autor",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    solicitacao_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("solicitacoes_titulares.id"), nullable=False, index=True
    )
    autor_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("usuarios.id"))
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
