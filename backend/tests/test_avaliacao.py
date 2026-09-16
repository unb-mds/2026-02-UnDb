import os
import unittest
from uuid import uuid4

from pydantic import ValidationError
from sqlalchemy import CheckConstraint, UniqueConstraint

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://teste:teste@localhost:5432/teste",
)
os.environ.setdefault("SECRET_KEY", "teste-local")

from app.models.avaliacao import Avaliacao
from app.models.enums import Dificuldade, QualidadeMaterial
from app.schemas.avaliacao import AvaliacaoCreate


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


if __name__ == "__main__":
    unittest.main()
