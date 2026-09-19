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
from app.repositories.avaliacao_repository import listar_por_professor_e_disciplina
from app.repositories.turma_repository import existe_vinculo_professor_disciplina
from app.models.enums import Dificuldade, QualidadeMaterial
from app.schemas.avaliacao import (
    AvaliacaoAgregadaInsuficienteResponse,
    AvaliacaoAgregadaSuficienteResponse,
)
from app.services.avaliacao_service import (
    RecursoNaoEncontradoError,
    consultar_agregado,
)


def registro(*, chamada: bool = True, material: bool = True) -> Mock:
    item = Mock()
    item.didatica = 4
    item.dificuldade = Dificuldade.MEDIO
    item.chamada = chamada
    item.disponibiliza_material = material
    item.qualidade_material = QualidadeMaterial.BOM if material else None
    item.recomenda = True
    return item


def professor(professor_id):
    return SimpleNamespace(
        id=professor_id,
        nome="PROFESSORA TESTE",
        departamento="CIC",
    )


def disciplina(disciplina_id):
    return SimpleNamespace(
        id=disciplina_id,
        codigo="CIC0001",
        nome="INTRODUCAO A CIENCIA DA COMPUTACAO",
        departamento="CIC",
    )


class ConsultaAgregadaServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock()
        self.professor_id = uuid4()
        self.disciplina_id = uuid4()
        patcher = patch("app.services.avaliacao_service.turma_repository")
        self.turma_repository = patcher.start()
        self.addCleanup(patcher.stop)
        self.turma_repository.existe_vinculo_professor_disciplina.return_value = True

    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_retorna_estado_vazio_sem_criterios(self, repository: Mock) -> None:
        repository.obter_professor.return_value = professor(self.professor_id)
        repository.obter_disciplina.return_value = disciplina(self.disciplina_id)
        repository.listar_por_professor_e_disciplina.return_value = []

        resultado = consultar_agregado(
            self.session,
            self.professor_id,
            self.disciplina_id,
        )

        self.assertEqual(resultado.total_avaliacoes, 0)
        self.assertFalse(resultado.dados_suficientes)
        self.assertIsNone(resultado.criterios)
        self.assertEqual(resultado.professor.nome, "PROFESSORA TESTE")
        self.assertEqual(resultado.disciplina.codigo, "CIC0001")

    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_nao_expoe_criterios_com_uma_ou_duas_avaliacoes(
        self,
        repository: Mock,
    ) -> None:
        repository.obter_professor.return_value = professor(self.professor_id)
        repository.obter_disciplina.return_value = disciplina(self.disciplina_id)

        for quantidade in (1, 2):
            with self.subTest(quantidade=quantidade):
                repository.listar_por_professor_e_disciplina.return_value = [
                    registro() for _ in range(quantidade)
                ]
                resultado = consultar_agregado(
                    self.session,
                    self.professor_id,
                    self.disciplina_id,
                )
                self.assertEqual(resultado.total_avaliacoes, quantidade)
                self.assertFalse(resultado.dados_suficientes)
                self.assertIsNone(resultado.criterios)

    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_retorna_agregado_a_partir_de_tres_avaliacoes(
        self,
        repository: Mock,
    ) -> None:
        repository.obter_professor.return_value = professor(self.professor_id)
        repository.obter_disciplina.return_value = disciplina(self.disciplina_id)
        repository.listar_por_professor_e_disciplina.return_value = [
            registro(),
            registro(chamada=False, material=False),
            registro(),
        ]

        resultado = consultar_agregado(
            self.session,
            self.professor_id,
            self.disciplina_id,
        )

        self.assertEqual(resultado.total_avaliacoes, 3)
        self.assertTrue(resultado.dados_suficientes)
        self.assertIsNotNone(resultado.criterios)
        self.assertIs(resultado.criterios.chamada, True)

    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_rejeita_professor_ou_disciplina_inexistente(self, repository: Mock) -> None:
        repository.obter_professor.return_value = None
        with self.assertRaisesRegex(RecursoNaoEncontradoError, "professor"):
            consultar_agregado(self.session, self.professor_id, self.disciplina_id)

        repository.obter_professor.return_value = professor(self.professor_id)
        repository.obter_disciplina.return_value = None
        with self.assertRaisesRegex(RecursoNaoEncontradoError, "disciplina"):
            consultar_agregado(self.session, self.professor_id, self.disciplina_id)

    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_rejeita_professor_sem_vinculo_com_disciplina(
        self, repository: Mock
    ) -> None:
        repository.obter_professor.return_value = professor(self.professor_id)
        repository.obter_disciplina.return_value = disciplina(self.disciplina_id)
        self.turma_repository.existe_vinculo_professor_disciplina.return_value = False

        with self.assertRaisesRegex(RecursoNaoEncontradoError, "vinculo"):
            consultar_agregado(self.session, self.professor_id, self.disciplina_id)

        repository.listar_por_professor_e_disciplina.assert_not_called()


class ConsultaAgregadaRepositoryTest(unittest.TestCase):
    def test_filtra_simultaneamente_por_professor_e_disciplina(self) -> None:
        db = Mock()
        db.scalars.return_value.all.return_value = []
        professor_id = uuid4()
        disciplina_id = uuid4()

        resultado = listar_por_professor_e_disciplina(
            db,
            professor_id,
            disciplina_id,
        )

        self.assertEqual(resultado, [])
        consulta = db.scalars.call_args.args[0]
        parametros = set(consulta.compile().params.values())
        self.assertEqual(parametros, {professor_id, disciplina_id})

    def test_verifica_vinculo_por_professor_e_disciplina(self) -> None:
        db = Mock()
        consulta = db.query.return_value.join.return_value.filter.return_value
        consulta.first.return_value = object()
        professor_id = uuid4()
        disciplina_id = uuid4()

        resultado = existe_vinculo_professor_disciplina(
            db,
            professor_id,
            disciplina_id,
        )

        self.assertTrue(resultado)

        expressoes = db.query.return_value.join.return_value.filter.call_args.args
        parametros = {
            valor
            for expressao in expressoes
            for valor in expressao.compile().params.values()
        }

        self.assertTrue({professor_id, disciplina_id} <= parametros)


class ConsultaAgregadaContratoTest(unittest.TestCase):
    def test_endpoint_publico_esta_registrado(self) -> None:
        operacoes = app.openapi()["paths"][
            "/api/professores/{professor_id}/disciplinas/{disciplina_id}"
        ]
        self.assertIn("get", operacoes)

    def test_resposta_insuficiente_omite_todos_os_criterios(self) -> None:
        resposta = AvaliacaoAgregadaInsuficienteResponse(
            professor_id=uuid4(),
            disciplina_id=uuid4(),
            professor={
                "id": uuid4(),
                "nome": "PROFESSORA TESTE",
                "departamento": "CIC",
            },
            disciplina={
                "id": uuid4(),
                "codigo": "CIC0001",
                "nome": "INTRODUCAO A CIENCIA DA COMPUTACAO",
                "departamento": "CIC",
            },
            total_avaliacoes=2,
            dados_suficientes=False,
        ).model_dump()

        self.assertEqual(
            set(resposta),
            {
                "professor_id",
                "disciplina_id",
                "professor",
                "disciplina",
                "total_avaliacoes",
                "dados_suficientes",
            },
        )

    def test_resposta_suficiente_preserva_qualidade_nula(self) -> None:
        resposta = AvaliacaoAgregadaSuficienteResponse(
            professor_id=uuid4(),
            disciplina_id=uuid4(),
            professor={
                "id": uuid4(),
                "nome": "PROFESSORA TESTE",
                "departamento": "CIC",
            },
            disciplina={
                "id": uuid4(),
                "codigo": "CIC0001",
                "nome": "INTRODUCAO A CIENCIA DA COMPUTACAO",
                "departamento": "CIC",
            },
            total_avaliacoes=4,
            dados_suficientes=True,
            didatica=4.0,
            dificuldade="MEDIO",
            chamada="CONFLITANTE",
            disponibiliza_material=False,
            qualidade_material=None,
            recomenda=50,
        ).model_dump()

        self.assertIn("qualidade_material", resposta)
        self.assertIsNone(resposta["qualidade_material"])


if __name__ == "__main__":
    unittest.main()
