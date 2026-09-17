import unittest
from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import patch

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Disciplina, Professor, Turma, Unidade  # noqa: F401
from app.scrapers.sigaa_poc import Oferta
from app.services.sigaa_import_service import (
    DepartamentoImportacao,
    executar_importacao,
    salvar_oferta,
)


def _oferta(
    *docentes: str, turma: str = "01", componente_id: str = "123"
) -> Oferta:
    return Oferta(
        componente_codigo="CIC0001",
        componente_nome="INTRODUCAO A CIENCIA DA COMPUTACAO",
        turma_codigo=turma,
        periodo="2026.2",
        docentes=docentes,
        componente_id=componente_id,
        unidade_id="637",
    )


class SigaaImportServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_persiste_zero_um_ou_multiplos_docentes(self) -> None:
        with Session(self.engine) as db:
            sem_docente = salvar_oferta(db, _oferta(turma="01"), "CIC")
            um_docente = salvar_oferta(db, _oferta("DOCENTE UM", turma="02"), "CIC")
            varios = salvar_oferta(
                db, _oferta("DOCENTE UM", "DOCENTE DOIS", turma="03"), "CIC"
            )
            db.commit()
            self.assertEqual(len(sem_docente.professores), 0)
            self.assertEqual(len(um_docente.professores), 1)
            self.assertEqual(len(varios.professores), 2)
            self.assertEqual(db.scalar(select(func.count(Turma.id))), 3)

    def test_reimportacao_e_idempotente_e_sincroniza_docentes(self) -> None:
        with Session(self.engine) as db:
            primeira = salvar_oferta(db, _oferta("DOCENTE UM"), "CIC")
            db.commit()
            primeira_id = primeira.id
            primeira.ultima_observacao_em = datetime(2000, 1, 1, tzinfo=UTC)
            db.commit()
            segunda = salvar_oferta(db, _oferta("DOCENTE DOIS"), "CIC")
            db.commit()
            self.assertEqual(segunda.id, primeira_id)
            self.assertEqual([p.nome for p in segunda.professores], ["DOCENTE DOIS"])
            self.assertGreater(
                segunda.ultima_observacao_em.replace(tzinfo=UTC),
                datetime(2000, 1, 1, tzinfo=UTC),
            )
            self.assertEqual(db.scalar(select(func.count(Turma.id))), 1)

    def test_recusa_troca_silenciosa_de_identificador_da_unidade(self) -> None:
        with Session(self.engine) as db:
            salvar_oferta(db, _oferta("DOCENTE", turma="01"), "CIC")
            db.commit()

            oferta_conflitante = replace(
                _oferta("DOCENTE", turma="02"),
                unidade_id="999",
            )
            with self.assertRaisesRegex(ValueError, "conflito de identidade da unidade"):
                salvar_oferta(db, oferta_conflitante, "CIC")

            unidade = db.scalar(select(Unidade))
            self.assertEqual(unidade.identificador_externo, "637")

    def test_recusa_identificador_da_unidade_associado_a_outro_codigo(self) -> None:
        with Session(self.engine) as db:
            salvar_oferta(db, _oferta("DOCENTE", turma="01"), "CIC")
            db.commit()

            with self.assertRaisesRegex(ValueError, "ja pertence a outro codigo"):
                salvar_oferta(db, _oferta("DOCENTE", turma="02"), "MAT")

            self.assertEqual(db.scalar(select(func.count(Unidade.id))), 1)

    def test_homonimos_sem_siape_nao_sao_unidos(self) -> None:
        with Session(self.engine) as db:
            salvar_oferta(db, _oferta("DOCENTE HOMONIMO", turma="01"), "CIC")
            salvar_oferta(db, _oferta("DOCENTE HOMONIMO", turma="02"), "CIC")
            db.commit()
            professores = list(db.scalars(select(Professor)).all())
            self.assertEqual(len(professores), 2)
            self.assertTrue(all(not p.identidade_confirmada for p in professores))
            self.assertEqual(len({p.identidade_origem for p in professores}), 2)

    def test_recusa_departamento_ausente_antes_de_escrever(self) -> None:
        with Session(self.engine) as db:
            with self.assertRaisesRegex(ValueError, "departamento"):
                salvar_oferta(db, _oferta("DOCENTE"), "   ")


class ExecucaoImportacaoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_falha_de_coleta_nao_impede_unidade_seguinte(self) -> None:
        def coletor(unidade: str, ano: str, periodo: str):
            if unidade == "UNIDADE COM FALHA":
                raise RuntimeError("SIGAA indisponivel")
            return [_oferta("PROFESSORA TESTE")], 1

        with Session(self.engine) as db:
            resultado = executar_importacao(
                db,
                [
                    DepartamentoImportacao("FALHA", "UNIDADE COM FALHA"),
                    DepartamentoImportacao("CIC", "DEPTO CIENCIAS DA COMPUTACAO"),
                ],
                "2026",
                "2",
                coletor,
            )
            self.assertFalse(resultado.sucesso)
            self.assertFalse(resultado.departamentos[0].sucesso)
            self.assertTrue(resultado.departamentos[1].sucesso)
            self.assertEqual(db.scalar(select(func.count(Turma.id))), 1)

    def test_coleta_completa_inativa_ausentes(self) -> None:
        with Session(self.engine) as db:
            executar_importacao(
                db, [DepartamentoImportacao("CIC", "CIC")], "2026", "2",
                coletor=lambda *_: (
                    [_oferta("DOCENTE", turma="01"), _oferta("DOCENTE", turma="02")], 2
                ),
            )
            executar_importacao(
                db, [DepartamentoImportacao("CIC", "CIC")], "2026", "2",
                coletor=lambda *_: ([_oferta("DOCENTE", turma="01")], 1),
            )
            turmas = list(db.scalars(select(Turma).order_by(Turma.codigo)).all())
            self.assertEqual([turma.ativa for turma in turmas], [True, False])

    def test_coleta_parcial_nunca_inativa_ausentes(self) -> None:
        with Session(self.engine) as db:
            executar_importacao(
                db, [DepartamentoImportacao("CIC", "CIC")], "2026", "2",
                coletor=lambda *_: (
                    [_oferta("DOCENTE", turma="01"), _oferta("DOCENTE", turma="02")], 2
                ),
            )
            resultado = executar_importacao(
                db, [DepartamentoImportacao("CIC", "CIC")], "2026", "2",
                coletor=lambda *_: ([_oferta("DOCENTE", turma="01")], 2),
            )
            self.assertEqual(resultado.departamentos[0].estado, "parcial")
            self.assertTrue(all(db.scalars(select(Turma.ativa)).all()))

    def test_resultado_e_serializavel_para_a_rotina_26(self) -> None:
        with Session(self.engine) as db:
            resultado = executar_importacao(
                db, [DepartamentoImportacao("CIC", "CIC")], "2026", "2",
                coletor=lambda *_: ([], 0),
            ).to_dict()
        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["departamentos"][0]["estado"], "sucesso")

    def test_total_ausente_impede_sucesso_silencioso(self) -> None:
        with Session(self.engine) as db:
            resultado = executar_importacao(
                db, [DepartamentoImportacao("CIC", "CIC")], "2026", "2",
                coletor=lambda *_: ([], None),
            )
        self.assertFalse(resultado.sucesso)
        self.assertIn("nao informado", resultado.departamentos[0].erros[0])

    def test_exige_ao_menos_um_departamento(self) -> None:
        with Session(self.engine) as db:
            with self.assertRaisesRegex(ValueError, "ao menos um departamento"):
                executar_importacao(db, [], "2026", "2", coletor=lambda *_: ([], 0))


class _SessionComCommitFalho:
    def begin_nested(self):
        return nullcontext()

    def commit(self) -> None:
        raise RuntimeError("banco indisponivel")

    def rollback(self) -> None:
        pass


class FalhaPersistenciaTest(unittest.TestCase):
    @patch("app.services.sigaa_import_service.unidade_repository.get_by_fonte_codigo")
    @patch("app.services.sigaa_import_service.salvar_oferta")
    def test_falha_de_commit_e_reportada(self, salvar, obter_unidade) -> None:
        obter_unidade.return_value = None
        resultado = executar_importacao(
            _SessionComCommitFalho(),
            [DepartamentoImportacao("CIC", "CIC")],
            "2026",
            "2",
            coletor=lambda *_: ([_oferta("DOCENTE")], 1),
        )
        self.assertFalse(resultado.sucesso)
        self.assertEqual(resultado.departamentos[0].ofertas_processadas, 0)
        self.assertIn("banco indisponivel", resultado.departamentos[0].erros[0])


if __name__ == "__main__":
    unittest.main()
