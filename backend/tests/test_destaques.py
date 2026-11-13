import os
import unittest
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.main import app
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade, QualidadeMaterial
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.services.institucional_service import listar_destaques


class DestaquesTest(unittest.TestCase):
    def test_ordena_por_volume_sem_nota_geral_e_limita_a_seis(self):
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            professor = Professor(id=uuid4(), nome="Teste", departamento="TEST")
            db.add(professor)
            for i in range(8):
                d = Disciplina(
                    id=uuid4(), codigo=f"T{i}", nome=f"Disciplina {i}", departamento="TEST"
                )
                db.add(d)
                for j in range(i):
                    u = Usuario(
                        id=uuid4(),
                        nome="Teste",
                        email=f"{i}-{j}@aluno.unb.br",
                        password_hash="teste",
                    )
                    db.add(u)
                    db.add(
                        Avaliacao(
                            usuario_id=u.id,
                            professor_id=professor.id,
                            disciplina_id=d.id,
                            didatica=1 if i == 7 else 5,
                            dificuldade=Dificuldade.MEDIO,
                            chamada=False,
                            disponibiliza_material=True,
                            qualidade_material=QualidadeMaterial.BOM,
                            recomenda=i != 7,
                        )
                    )
            db.commit()
            dados = listar_destaques(db)
            self.assertEqual([d.total_avaliacoes for d in dados], [7, 6, 5, 4, 3, 2])
            self.assertEqual(dados[0].codigo, "T7")
            self.assertNotIn("didatica", dados[0].model_dump())
            self.assertNotIn("recomenda", dados[0].model_dump())
        engine.dispose()

    def test_sem_avaliacoes_retorna_lista_vazia(self):
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            db.add(Disciplina(id=uuid4(), codigo="V0", nome="Sem avaliações", departamento="TEST"))
            db.commit()
            self.assertEqual(listar_destaques(db), [])
        engine.dispose()

    def test_rota_destaques_vem_antes_da_rota_por_id(self):
        caminhos = [getattr(rota, "path", "") for rota in app.routes]
        self.assertLess(
            caminhos.index("/api/disciplinas/destaques"),
            caminhos.index("/api/disciplinas/{disciplina_id}"),
        )
