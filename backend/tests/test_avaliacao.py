import os
import unittest
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, UniqueConstraint, create_engine, func, select
from sqlalchemy.orm import Session

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://teste:teste@localhost:5432/teste",
)
os.environ.setdefault("SECRET_KEY", "teste-local")

from app.core.database import Base
from app.main import app
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade, QualidadeMaterial
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.routers import avaliacoes as avaliacoes_router
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoResponse
from app.services import avaliacao_service


class AvaliacaoSchemaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "professor_id": str(uuid4()),
            "disciplina_id": str(uuid4()),
            "didatica": 3,
            "dificuldade": "MEDIO",
            "chamada": True,
            "disponibiliza_material": True,
            "qualidade_material": "BOM",
            "recomenda": True,
        }

    def test_aceita_todas_as_escalas_definidas(self) -> None:
        for didatica in (1, 5):
            for dificuldade in Dificuldade:
                with self.subTest(didatica=didatica, dificuldade=dificuldade):
                    avaliacao = AvaliacaoCreate.model_validate(
                        {
                            **self.payload,
                            "didatica": didatica,
                            "dificuldade": dificuldade.value,
                        }
                    )
                    self.assertEqual(avaliacao.didatica, didatica)
                    self.assertEqual(avaliacao.dificuldade, dificuldade)

        for qualidade in QualidadeMaterial:
            with self.subTest(qualidade=qualidade):
                avaliacao = AvaliacaoCreate.model_validate(
                    {**self.payload, "qualidade_material": qualidade.value}
                )
                self.assertEqual(avaliacao.qualidade_material, qualidade)

        payload_sem_material = {
            **self.payload,
            "disponibiliza_material": False,
        }
        payload_sem_material.pop("qualidade_material")
        sem_material = AvaliacaoCreate.model_validate(payload_sem_material)
        self.assertIsNone(sem_material.qualidade_material)

    def test_rejeita_didatica_fora_da_escala_ou_nao_inteira(self) -> None:
        for valor in (0, 6, "3", 3.0, True):
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                AvaliacaoCreate.model_validate({**self.payload, "didatica": valor})

    def test_rejeita_valores_fora_dos_enums(self) -> None:
        for campo, valor in (
            ("dificuldade", "CONFLITANTE"),
            ("dificuldade", "MUITO_DIFICIL"),
            ("qualidade_material", "EXCELENTE"),
            ("qualidade_material", "NAO_DISPONIBILIZA"),
        ):
            with self.subTest(campo=campo, valor=valor), self.assertRaises(ValidationError):
                AvaliacaoCreate.model_validate({**self.payload, campo: valor})

    def test_rejeita_coercao_de_campos_booleanos(self) -> None:
        for campo in ("chamada", "disponibiliza_material", "recomenda"):
            for valor in (0, 1, "sim", "nao", "true", "false"):
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValidationError):
                    AvaliacaoCreate.model_validate({**self.payload, campo: valor})

    def test_exige_qualidade_apenas_quando_material_e_disponibilizado(self) -> None:
        casos_invalidos = (
            {**self.payload, "qualidade_material": None},
            {
                **self.payload,
                "disponibiliza_material": False,
                "qualidade_material": "RUIM",
            },
        )

        for payload in casos_invalidos:
            with self.subTest(payload=payload), self.assertRaisesRegex(
                ValidationError,
                "qualidade_material e obrigatoria",
            ):
                AvaliacaoCreate.model_validate(payload)

    def test_rejeita_campos_fora_do_formulario_da_release_1(self) -> None:
        for campo in ("comentario", "nota_geral", "usuario_id", "created_at"):
            with self.subTest(campo=campo), self.assertRaises(ValidationError):
                AvaliacaoCreate.model_validate({**self.payload, campo: "nao permitido"})


class AvaliacaoModelTest(unittest.TestCase):
    def test_modelo_contem_identificacao_criterios_e_datas(self) -> None:
        self.assertEqual(
            set(Avaliacao.__table__.columns.keys()),
            {
                "id",
                "usuario_id",
                "professor_id",
                "disciplina_id",
                "didatica",
                "dificuldade",
                "chamada",
                "disponibiliza_material",
                "qualidade_material",
                "recomenda",
                "created_at",
                "updated_at",
            },
        )

        for coluna in (
            "usuario_id",
            "professor_id",
            "disciplina_id",
            "didatica",
            "dificuldade",
            "chamada",
            "disponibiliza_material",
            "recomenda",
            "created_at",
            "updated_at",
        ):
            with self.subTest(coluna=coluna):
                self.assertFalse(Avaliacao.__table__.columns[coluna].nullable)

    def test_modelo_garante_unicidade_por_usuario_professor_disciplina(self) -> None:
        constraint = next(
            item
            for item in Avaliacao.__table__.constraints
            if isinstance(item, UniqueConstraint)
            and item.name == "uq_avaliacao_usuario_professor_disciplina"
        )

        self.assertEqual(
            tuple(coluna.name for coluna in constraint.columns),
            ("usuario_id", "professor_id", "disciplina_id"),
        )

    def test_modelo_materializa_regras_de_escala_e_material(self) -> None:
        checks = {
            item.name: str(item.sqltext)
            for item in Avaliacao.__table__.constraints
            if isinstance(item, CheckConstraint)
        }

        self.assertEqual(checks["ck_avaliacao_didatica"], "didatica BETWEEN 1 AND 5")
        self.assertIn("qualidade_material IS NOT NULL", checks["ck_avaliacao_qualidade_material"])
        self.assertIn("qualidade_material IS NULL", checks["ck_avaliacao_qualidade_material"])

    def test_modelo_referencia_usuario_professor_e_disciplina(self) -> None:
        referencias = {
            coluna.name: next(iter(coluna.foreign_keys)).target_fullname
            for coluna in (
                Avaliacao.__table__.columns.usuario_id,
                Avaliacao.__table__.columns.professor_id,
                Avaliacao.__table__.columns.disciplina_id,
            )
        }

        self.assertEqual(
            referencias,
            {
                "usuario_id": "usuarios.id",
                "professor_id": "professores.id",
                "disciplina_id": "disciplinas.id",
            },
        )


class RegistroAvaliacaoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.usuario = Usuario(
            nome="Maria",
            email="maria@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=True,
        )
        self.professor = Professor(nome="Professora Teste", departamento="CIC")
        self.disciplina = Disciplina(
            codigo="CIC0001",
            nome="Disciplina Teste",
            departamento="CIC",
        )
        self.db.add_all((self.usuario, self.professor, self.disciplina))
        self.db.commit()
        self.dados = AvaliacaoCreate(
            professor_id=self.professor.id,
            disciplina_id=self.disciplina.id,
            didatica=4,
            dificuldade="MEDIO",
            chamada=True,
            disponibiliza_material=True,
            qualidade_material="BOM",
            recomenda=True,
        )

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_envio_valido_persiste_avaliador_e_retorna_schema(self) -> None:
        resposta = avaliacoes_router.registrar_avaliacao(
            self.dados,
            self.usuario,
            self.db,
        )

        registro = self.db.scalar(select(Avaliacao))
        self.assertIsInstance(resposta, AvaliacaoResponse)
        self.assertEqual(registro.usuario_id, self.usuario.id)
        self.assertEqual(resposta.id, registro.id)
        self.assertNotIn("usuario_id", resposta.model_dump())
        self.assertIsNotNone(resposta.created_at)
        self.assertIsNotNone(resposta.updated_at)

    def test_novo_envio_substitui_sem_duplicar_e_atualiza_updated_at(self) -> None:
        primeira = avaliacao_service.registrar_avaliacao(
            self.db,
            self.usuario,
            self.dados,
        )
        id_original = primeira.id
        created_at_original = primeira.created_at
        instante_antigo = datetime(2000, 1, 1, tzinfo=timezone.utc)
        primeira.updated_at = instante_antigo
        self.db.commit()

        substituida = avaliacao_service.registrar_avaliacao(
            self.db,
            self.usuario,
            self.dados.model_copy(
                update={
                    "didatica": 1,
                    "dificuldade": Dificuldade.DIFICIL,
                    "chamada": False,
                    "disponibiliza_material": False,
                    "qualidade_material": None,
                    "recomenda": False,
                }
            ),
        )

        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual(quantidade, 1)
        self.assertEqual(substituida.id, id_original)
        self.assertEqual(substituida.created_at, created_at_original)
        self.assertNotEqual(substituida.updated_at, instante_antigo)
        self.assertEqual(substituida.didatica, 1)
        self.assertFalse(substituida.disponibiliza_material)
        self.assertIsNone(substituida.qualidade_material)

    def test_rejeita_professor_ou_disciplina_inexistente_sem_persistir(self) -> None:
        casos = (
            ("professor", self.dados.model_copy(update={"professor_id": uuid4()})),
            ("disciplina", self.dados.model_copy(update={"disciplina_id": uuid4()})),
        )
        for recurso, dados in casos:
            with self.subTest(recurso=recurso), self.assertRaisesRegex(
                avaliacao_service.RecursoNaoEncontradoError,
                recurso,
            ):
                avaliacao_service.registrar_avaliacao(self.db, self.usuario, dados)

        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual(quantidade, 0)

    def test_router_traduz_referencia_inexistente_para_404(self) -> None:
        with self.assertRaises(HTTPException) as contexto:
            avaliacoes_router.registrar_avaliacao(
                self.dados.model_copy(update={"professor_id": uuid4()}),
                self.usuario,
                self.db,
            )

        self.assertEqual(contexto.exception.status_code, 404)

    def test_contrato_post_avaliacoes_esta_no_openapi(self) -> None:
        operacoes = app.openapi()["paths"]["/api/avaliacoes"]
        rota = avaliacoes_router.router.routes[0]

        self.assertIn("post", operacoes)
        self.assertIn(
            "obter_usuario_confirmado",
            {dependencia.call.__name__ for dependencia in rota.dependant.dependencies},
        )
        self.assertEqual(
            operacoes["post"]["responses"]["200"]["content"]["application/json"][
                "schema"
            ]["$ref"],
            "#/components/schemas/AvaliacaoResponse",
        )


if __name__ == "__main__":
    unittest.main()
