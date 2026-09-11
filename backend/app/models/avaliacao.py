from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

class Avaliacao(Base):
    __tablename__ = "avaliacao"

    id_review = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.matricula"), nullable=False)
    id_turma = Column(Integer, ForeignKey("turma.id_turma"), nullable=False)

    didatica = Column(Integer, nullable=False)
    qualidade_material = Column(Integer, nullable=True)
    chamada = Column(Integer, nullable=False)
    recomenda = Column(Boolean, nullable=False)
    disponibiliza_material = Column(Boolean, nullable=False)
    dificuldade = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)

    usuario = relationship("Usuario", back_populates="avaliacoes")
    turma = relationship("Turma", back_populates="avaliacoes")

    __table_args__ = (
        UniqueConstraint("id_usuario", "id_turma", name="uq_usuario_turma_avaliacao"),
    )