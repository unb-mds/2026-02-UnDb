from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.session import Base

estuda = Table(
    "estuda",
    Base.metadata,
    Column("matricula", Integer, ForeignKey("usuario.matricula"), primary_key=True),
    Column("id_disciplinas", Integer, ForeignKey("disciplinas.id_disciplinas"), primary_key=True),
)

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id_disciplinas = Column(Integer, primary_key=True, index=True)
    id_departamento = Column(Integer, ForeignKey("departamento.id_dpto"), nullable=False)
    codigo = Column(String(20), nullable=False, unique=True)
    nome = Column(String(150), nullable=False)

    departamento = relationship("Departamento", back_populates="disciplinas")
    turmas = relationship("Turma", back_populates="disciplina")
    alunos = relationship("Usuario", secondary=estuda, back_populates="disciplinas_cursadas")