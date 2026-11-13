import asyncio
import os
import unittest
from uuid import uuid4
from unittest.mock import patch

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

    def test_rota_destaques_nao_e_capturada_como_id(self):
        # Verifica o contrato HTTP, sem depender da representação interna dos routers.
        mensagens = []

        async def solicitar():
            async def receive():
                return {"type": "http.request", "body": b"", "more_body": False}

            async def send(mensagem):
                mensagens.append(mensagem)

            await app(
                {
                    "type": "http",
                    "asgi": {"version": "3.0"},
                    "http_version": "1.1",
                    "method": "GET",
                    "scheme": "http",
                    "path": "/api/disciplinas/destaques",
                    "raw_path": b"/api/disciplinas/destaques",
                    "query_string": b"",
                    "headers": [],
                    "client": ("127.0.0.1", 12345),
                    "server": ("testserver", 80),
                    "root_path": "",
                    "state": {},
                },
                receive,
                send,
            )

        with patch(
            "app.services.institucional_service.listar_destaques", return_value=[]
        ) as listar:
            asyncio.run(solicitar())
        inicio = next(m for m in mensagens if m["type"] == "http.response.start")
        corpo = b"".join(m.get("body", b"") for m in mensagens if m["type"] == "http.response.body")
        self.assertEqual(inicio["status"], 200)
        self.assertEqual(corpo, b"[]")
        listar.assert_called_once()
