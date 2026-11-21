import os
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://teste:teste@localhost:5432/teste",
)
os.environ.setdefault("SECRET_KEY", "teste-local")

from app.core.database import Base
from app.domain.avaliacoes import (
    AvaliacaoParaAgregacao,
    ContagensAvaliacoes,
    Dificuldade,
    QualidadeMaterial,
    agregar_avaliacoes,
    agregar_contagens,
)
from app.main import app
from app.models.avaliacao import Avaliacao
from app.repositories.avaliacao_repository import contar_por_disciplina_e_professores
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
        departamento_nome=None,
    )


def professor(professor_id, nome):
    return SimpleNamespace(id=professor_id, nome=nome, departamento="CIC", departamento_nome=None)


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
        avaliacao_repository.contar_por_disciplina_e_professores.return_value = {
            self.professor_alice.id: ContagensAvaliacoes(3, 12, (0, 3, 0), 3, 3, (0, 0, 3), 3),
            self.professor_bruno.id: ContagensAvaliacoes(4, 16, (0, 4, 0), 4, 4, (0, 0, 4), 4),
        }

        resultado = comparar_professores(self.session, self.disciplina_id)

        avaliacao_repository.contar_por_disciplina_e_professores.assert_called_once_with(
            self.session,
            self.disciplina_id,
            [self.professor_alice.id, self.professor_bruno.id, self.professor_carol.id],
        )
        self.turma_repository.existe_vinculo_professor_disciplina.assert_not_called()
        self.assertEqual(resultado.disciplina.id, self.disciplina_id)
        self.assertEqual(
            [consulta.professor.nome for consulta in resultado.professores],
            ["Bruno", "Alice", "Carol"],
        )
        self.assertEqual(resultado.professores[0].criterios.recomenda, 100)
        self.assertFalse(resultado.professores[-1].dados_suficientes)
        self.assertEqual(resultado.professores[-1].total_avaliacoes, 0)

    @patch("app.services.avaliacao_service.avaliacao_repository")
    def test_rejeita_disciplina_inexistente(self, avaliacao_repository: Mock) -> None:
        avaliacao_repository.obter_disciplina.return_value = None

        with self.assertRaisesRegex(RecursoNaoEncontradoError, "disciplina"):
            comparar_professores(self.session, self.disciplina_id)


class ComparacaoProfessoresRepositoryTest(unittest.TestCase):
    def test_contagens_sql_equivalem_a_agregacao_das_avaliacoes(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        self.addCleanup(engine.dispose)
        Base.metadata.create_all(engine)
        professor_id, outro_professor_id, disciplina_id = uuid4(), uuid4(), uuid4()
        respostas = [
            AvaliacaoParaAgregacao(1, Dificuldade.FACIL, True, True, QualidadeMaterial.RUIM, True),
            AvaliacaoParaAgregacao(1, Dificuldade.MEDIO, True, True, QualidadeMaterial.MEDIO, True),
            AvaliacaoParaAgregacao(
                1, Dificuldade.DIFICIL, False, True, QualidadeMaterial.BOM, False
            ),
            AvaliacaoParaAgregacao(2, Dificuldade.FACIL, False, False, None, False),
        ]

        with Session(engine) as db:
            for resposta in respostas:
                db.add(
                    Avaliacao(
                        usuario_id=uuid4(),
                        professor_id=professor_id,
                        disciplina_id=disciplina_id,
                        **vars(resposta),
                    )
                )
            db.add(
                Avaliacao(
                    usuario_id=uuid4(),
                    professor_id=professor_id,
                    disciplina_id=uuid4(),
                    **vars(respostas[0]),
                )
            )
            db.add(
                Avaliacao(
                    usuario_id=uuid4(),
                    professor_id=professor_id,
                    disciplina_id=disciplina_id,
                    excluido_em=datetime.now(timezone.utc),
                    **vars(respostas[0]),
                )
            )
            db.flush()
            contagens = contar_por_disciplina_e_professores(
                db, disciplina_id, [professor_id, outro_professor_id]
            )

        self.assertEqual(set(contagens), {professor_id})
        self.assertEqual(contagens[professor_id].total, 4)
        self.assertEqual(agregar_contagens(contagens[professor_id]), agregar_avaliacoes(respostas))

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
        operacao = app.openapi()["paths"]["/api/disciplinas/{disciplina_id}/professores"]["get"]

        parametro = next(
            parametro for parametro in operacao["parameters"] if parametro["name"] == "ordenar_por"
        )
        self.assertTrue(parametro["required"])
        self.assertEqual(parametro["schema"]["const"], "recomendacao")


if __name__ == "__main__":
    unittest.main()
