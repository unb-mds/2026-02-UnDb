from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.disciplina import estuda

class Usuario(Base):
    __tablename__ = "usuario"

    matricula = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)

    avaliacoes = relationship("Avaliacao", back_populates="usuario")
    disciplinas_cursadas = relationship("Disciplina", secondary=estuda, back_populates="alunos")