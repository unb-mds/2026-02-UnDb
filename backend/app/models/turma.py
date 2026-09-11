from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


class Turma(Base):
    __tablename__ = "turma"

    id_turma = Column(Integer, primary_key=True, index=True)
    id_disciplinas = Column(Integer, ForeignKey("disciplinas.id_disciplinas"), nullable=False)
    id_professor = Column(Integer, ForeignKey("professor.id_professor"), nullable=False)
    semestre = Column(String(10), nullable=False)
    cod_turma = Column(String(10), nullable=False)
    horario = Column(String, nullable=True)

    disciplina = relationship("Disciplina", back_populates="turmas")
    professor = relationship("Professor", back_populates="turmas")
    avaliacoes = relationship("Avaliacao", back_populates="turma")

    __table_args__ = (
        UniqueConstraint(
            "id_disciplinas",
            "cod_turma",
            "semestre",
            name="uq_turma_disciplina_codigo_semestre",
        ),
    )
