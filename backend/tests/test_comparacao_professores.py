import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://teste:teste@localhost:5432/teste",
)
os.environ.setdefault("SECRET_KEY", "teste-local")

from app.main import app
from app.models.enums import Dificuldade, QualidadeMaterial
from app.repositories.professor_repository import listar_por_disciplina
from app.services.avaliacao_service import (
    RecursoNaoEncontradoError,
    comparar_professores,
)


def disciplina(disciplina_id):
    return SimpleNamespace(
        id=disciplina_id,
        codigo="CIC0001",
        nome="INTRODUCAO A CIENCIA DA COMPUTACAO",
        departamento="CIC",
    )


def professor(professor_id, nome):
    return SimpleNamespace(id=professor_id, nome=nome, departamento="CIC")


def avaliacao(recomenda: bool):
    return SimpleNamespace(
        didatica=4,
        dificuldade=Dificuldade.MEDIO,
        chamada=True,
        disponibiliza_material=True,
        qualidade_material=QualidadeMaterial.BOM,
        recomenda=recomenda,
    )


class ComparacaoProfessoresServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock()
        self.disciplina_id = uuid4()
        self.professor_alice = professor(uuid4(), "Alice")
        self.professor_bruno = professor(uuid4(), "Bruno")
        self.professor_carol = professor(uuid4(), "Carol")

        patcher = patch("app.services.avaliacao_service.turma_repository")
        self.turma_repository = patcher.start()
        self.addCleanup(patcher.stop)
        self.turma_repository.existe_vinculo_professor_disciplina.return_value = True

    @patch("app.services.avaliacao_service.professor_repository")
    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_ordena_por_recomendacao_total_e_nome(
        self, avaliacao_repository: Mock, professor_repository: Mock
    ) -> None:
        avaliacao_repository.obter_disciplina.return_value = disciplina(self.disciplina_id)
        professor_repository.listar_por_disciplina.return_value = [
            self.professor_alice,
            self.professor_bruno,
            self.professor_carol,
        ]
        avaliacao_repository.obter_professor.side_effect = lambda _, professor_id: {
            self.professor_alice.id: self.professor_alice,
            self.professor_bruno.id: self.professor_bruno,
            self.professor_carol.id: self.professor_carol,
        }[professor_id]
        avaliacao_repository.listar_por_professor_e_disciplina.side_effect = (
            lambda _, professor_id, __: {
                self.professor_alice.id: [avaliacao(True)] * 3,
                self.professor_bruno.id: [avaliacao(True)] * 4,
                self.professor_carol.id: [avaliacao(False)] * 2,
            }[professor_id]
        )

        resultado = comparar_professores(self.session, self.disciplina_id)

        self.assertEqual(resultado.disciplina.id, self.disciplina_id)
        self.assertEqual(
            [consulta.professor.nome for consulta in resultado.professores],
            ["Bruno", "Alice", "Carol"],
        )
        self.assertEqual(resultado.professores[0].criterios.recomenda, 100)
        self.assertFalse(resultado.professores[-1].dados_suficientes)

    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_rejeita_disciplina_inexistente(self, avaliacao_repository: Mock) -> None:
        avaliacao_repository.obter_disciplina.return_value = None

        with self.assertRaisesRegex(RecursoNaoEncontradoError, "disciplina"):
            comparar_professores(self.session, self.disciplina_id)


class ComparacaoProfessoresRepositoryTest(unittest.TestCase):
    def test_lista_professores_distintos_da_disciplina(self) -> None:
        db = Mock()
        db.scalars.return_value.all.return_value = []
        disciplina_id = uuid4()

        resultado = listar_por_disciplina(db, disciplina_id)

        self.assertEqual(resultado, [])
        consulta = db.scalars.call_args.args[0]
        self.assertIn(disciplina_id, consulta.compile().params.values())
        sql = str(consulta.compile())
        self.assertIn("JOIN turmas_professores", sql)
        self.assertIn("turmas.ativa IS true", sql)


class ComparacaoProfessoresContratoTest(unittest.TestCase):
    def test_endpoint_exige_a_chave_de_ordenacao_permitida(self) -> None:
        operacao = app.openapi()["paths"]["/api/disciplinas/{disciplina_id}/professores"][
            "get"
        ]

        parametro = next(
            parametro
            for parametro in operacao["parameters"]
            if parametro["name"] == "ordenar_por"
        )
        self.assertTrue(parametro["required"])
        self.assertEqual(parametro["schema"]["const"], "recomendacao")


if __name__ == "__main__":
    unittest.main()
