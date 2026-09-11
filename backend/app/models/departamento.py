from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


class Departamento(Base):
    __tablename__ = "departamento"

    id_dpto = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    sigla = Column(String(10), nullable=False)

    professores = relationship("Professor", back_populates="departamento")
    disciplinas = relationship("Disciplina", back_populates="departamento")

    __table_args__ = (
        UniqueConstraint("sigla", name="uq_departamento_sigla"),
    )
