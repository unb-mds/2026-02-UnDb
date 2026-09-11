from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Turma(Base):
    __tablename__ = "turma"

    id_turma = Column(Integer, primary_key=True, index=True)
    id_disciplinas = Column(Integer, ForeignKey("disciplinas.id_disciplinas"), nullable=False)
    id_professor = Column(Integer, ForeignKey("professor.id_professor"), nullable=False)
    semestre = Column(String(10), nullable=False)
    cod_turma = Column(String(10), nullable=False)

    disciplina = relationship("Disciplina", back_populates="turmas")
    professor = relationship("Professor", back_populates="turmas")
    avaliacoes = relationship("Avaliacao", back_populates="turma")