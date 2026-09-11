from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


class Professor(Base):
    __tablename__ = "professor"

    id_professor = Column(Integer, primary_key=True, index=True)
    id_departamento = Column(Integer, ForeignKey("departamento.id_dpto"), nullable=False)
    nome = Column(String(150), nullable=False)
    lattes = Column(String(255), nullable=True)
    email = Column(String(150), nullable=True)

    departamento = relationship("Departamento", back_populates="professores")
    turmas = relationship("Turma", back_populates="professor")

    __table_args__ = (
        UniqueConstraint(
            "nome",
            "id_departamento",
            name="uq_professor_nome_departamento",
        ),
    )
