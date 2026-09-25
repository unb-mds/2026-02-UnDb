import os
import unittest
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.main import app
from app.routers.disciplinas import obter_disciplina
from app.scrapers.sigaa_poc import Oferta
from app.services import institucional_service
from app.services.sigaa_import_service import salvar_oferta


class ApiInstitucionalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        salvar_oferta(
            self.db,
            Oferta(
                componente_codigo="CIC0002",
                componente_nome="FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO",
                turma_codigo="01",
                periodo="2026.2",
                docentes=("MARIA EMÍLIA",),
                componente_id="177942",
                unidade_id="637",
            ),
            "CIC",
            "DEPTO CIÊNCIAS DA COMPUTAÇÃO",
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_contrato_minimo_esta_no_openapi(self) -> None:
        caminhos = app.openapi()["paths"]
        esperados = {
            "/api/professores",
            "/api/professores/{professor_id}",
            "/api/professores/{professor_id}/disciplinas",
            "/api/disciplinas",
            "/api/disciplinas/{disciplina_id}",
            "/api/disciplinas/{disciplina_id}/turmas",
        }
        self.assertTrue(esperados <= set(caminhos))

    def test_busca_parcial_ignora_caixa_e_acentos(self) -> None:
        professores = institucional_service.listar_professores(
            self.db, "maria emilia"
        )
        disciplinas = institucional_service.listar_disciplinas(
            self.db, nome="teoricos computacao"
        )
        self.assertEqual(len(professores), 1)
        self.assertEqual(len(disciplinas), 1)

    def test_busca_sem_resultado_retorna_lista_vazia(self) -> None:
        self.assertEqual(
            institucional_service.listar_professores(self.db, "inexistente"), []
        )

    def test_recurso_individual_inexistente_retorna_404(self) -> None:
        with self.assertRaises(HTTPException) as contexto:
            obter_disciplina(uuid4(), self.db)
        self.assertEqual(contexto.exception.status_code, 404)

    def test_disponibiliza_relacoes_e_turmas(self) -> None:
        professor = institucional_service.listar_professores(self.db)[0]
        disciplina = institucional_service.listar_disciplinas(self.db)[0]
        disciplinas = institucional_service.listar_disciplinas_do_professor(
            self.db, professor.id
        )
        turmas = institucional_service.listar_turmas_da_disciplina(
            self.db, disciplina.id
        )
        self.assertEqual(disciplinas[0].codigo, "CIC0002")
        self.assertEqual(turmas[0].professores[0].nome, "MARIA EMÍLIA")


if __name__ == "__main__":
    unittest.main()
