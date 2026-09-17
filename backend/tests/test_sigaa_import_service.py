import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from app.scrapers.sigaa_poc import Oferta
from app.services.sigaa_import_service import (
    DepartamentoImportacao,
    OfertaNaoPersistivelError,
    executar_importacao,
    salvar_oferta,
)


def _oferta(*docentes: str) -> Oferta:
    return Oferta(
        componente_codigo="CIC0001",
        componente_nome="INTRODUCAO A CIENCIA DA COMPUTACAO",
        turma_codigo="01",
        periodo="2026.2",
        docentes=docentes,
        componente_id="123",
    )


class SigaaImportServiceTest(unittest.TestCase):
    @patch("app.services.sigaa_import_service.turma_repository")
    @patch("app.services.sigaa_import_service.professor_repository")
    @patch("app.services.sigaa_import_service.disciplina_repository")
    def test_persiste_oferta_com_departamento_explicito(
        self,
        disciplina_repository: Mock,
        professor_repository: Mock,
        turma_repository: Mock,
    ) -> None:
        db = Mock()
        disciplina = SimpleNamespace(id=uuid4())
        professor = SimpleNamespace(id=uuid4())
        turma = SimpleNamespace(id=uuid4())
        disciplina_repository.get_by_codigo.return_value = None
        disciplina_repository.create.return_value = disciplina
        professor_repository.get_by_nome_e_departamento.return_value = None
        professor_repository.create.return_value = professor
        turma_repository.get_by_disciplina_professor_semestre.return_value = None
        turma_repository.create.return_value = turma

        resultado = salvar_oferta(db, _oferta("PROFESSORA TESTE"), "  CIC  ")

        self.assertIs(resultado, turma)
        disciplina_repository.create.assert_called_once_with(
            db,
            codigo="CIC0001",
            nome="INTRODUCAO A CIENCIA DA COMPUTACAO",
            departamento="CIC",
        )
        professor_repository.get_by_nome_e_departamento.assert_called_once_with(
            db, "PROFESSORA TESTE", "CIC"
        )
        professor_repository.create.assert_called_once_with(
            db, "PROFESSORA TESTE", "CIC"
        )
        turma_repository.create.assert_called_once_with(
            db, disciplina.id, professor.id, "2026.2"
        )

    @patch("app.services.sigaa_import_service.turma_repository")
    @patch("app.services.sigaa_import_service.professor_repository")
    @patch("app.services.sigaa_import_service.disciplina_repository")
    def test_reutiliza_registros_existentes(
        self,
        disciplina_repository: Mock,
        professor_repository: Mock,
        turma_repository: Mock,
    ) -> None:
        db = Mock()
        disciplina = SimpleNamespace(id=uuid4())
        professor = SimpleNamespace(id=uuid4())
        turma = SimpleNamespace(id=uuid4())
        disciplina_repository.get_by_codigo.return_value = disciplina
        professor_repository.get_by_nome_e_departamento.return_value = professor
        turma_repository.get_by_disciplina_professor_semestre.return_value = turma

        resultado = salvar_oferta(db, _oferta("PROFESSORA TESTE"), "CIC")

        self.assertIs(resultado, turma)
        disciplina_repository.create.assert_not_called()
        professor_repository.create.assert_not_called()
        turma_repository.create.assert_not_called()

    @patch("app.services.sigaa_import_service.disciplina_repository")
    def test_recusa_multiplos_docentes_antes_de_escrever(
        self, disciplina_repository: Mock
    ) -> None:
        with self.assertRaisesRegex(OfertaNaoPersistivelError, "exatamente um docente"):
            salvar_oferta(Mock(), _oferta("DOCENTE UM", "DOCENTE DOIS"), "CIC")

        disciplina_repository.get_by_codigo.assert_not_called()
        disciplina_repository.create.assert_not_called()

    @patch("app.services.sigaa_import_service.disciplina_repository")
    def test_recusa_departamento_ausente_antes_de_escrever(
        self, disciplina_repository: Mock
    ) -> None:
        with self.assertRaisesRegex(OfertaNaoPersistivelError, "departamento"):
            salvar_oferta(Mock(), _oferta("PROFESSORA TESTE"), "   ")

        disciplina_repository.get_by_codigo.assert_not_called()
        disciplina_repository.create.assert_not_called()


class _SessionFalsa:
    def __init__(
        self,
        erro_commit: Exception | None = None,
        erro_rollback: Exception | None = None,
    ) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.erro_commit = erro_commit
        self.erro_rollback = erro_rollback

    def begin_nested(self):
        return nullcontext()

    def commit(self) -> None:
        self.commits += 1
        if self.erro_commit is not None:
            raise self.erro_commit

    def rollback(self) -> None:
        self.rollbacks += 1
        if self.erro_rollback is not None:
            raise self.erro_rollback


class ExecucaoImportacaoTest(unittest.TestCase):
    @patch("app.services.sigaa_import_service.salvar_oferta")
    def test_falha_de_coleta_nao_impede_departamento_seguinte(
        self, salvar: Mock
    ) -> None:
        session = _SessionFalsa()

        def coletor(unidade: str, ano: str, periodo: str):
            self.assertEqual((ano, periodo), ("2026", "2"))
            if unidade == "UNIDADE COM FALHA":
                raise RuntimeError("SIGAA indisponivel")
            return [_oferta("PROFESSORA TESTE")], 1

        resultado = executar_importacao(
            session,
            [
                DepartamentoImportacao("FALHA", "UNIDADE COM FALHA"),
                DepartamentoImportacao("CIC", "DEPTO CIENCIAS DA COMPUTACAO"),
            ],
            ano="2026",
            periodo="2",
            coletor=coletor,
        )

        self.assertFalse(resultado.sucesso)
        self.assertFalse(resultado.departamentos[0].sucesso)
        self.assertTrue(resultado.departamentos[1].sucesso)
        self.assertEqual(resultado.departamentos[1].ofertas_processadas, 1)
        self.assertEqual(session.rollbacks, 0)
        self.assertEqual(session.commits, 1)
        salvar.assert_called_once()

    @patch("app.services.sigaa_import_service.salvar_oferta")
    def test_falha_de_uma_oferta_e_registrada_sem_interromper_as_demais(
        self, salvar: Mock
    ) -> None:
        session = _SessionFalsa()
        salvar.side_effect = [
            OfertaNaoPersistivelError("multiplos docentes"),
            Mock(),
        ]
        ofertas = [
            _oferta("DOCENTE UM", "DOCENTE DOIS"),
            _oferta("PROFESSORA TESTE"),
        ]

        resultado = executar_importacao(
            session,
            [DepartamentoImportacao("CIC", "DEPTO CIENCIAS DA COMPUTACAO")],
            ano="2026",
            periodo="2",
            coletor=lambda *_: (ofertas, 2),
        )

        departamento = resultado.departamentos[0]
        self.assertFalse(resultado.sucesso)
        self.assertEqual(departamento.ofertas_extraidas, 2)
        self.assertEqual(departamento.ofertas_processadas, 1)
        self.assertEqual(len(departamento.erros), 1)
        self.assertIn("multiplos docentes", departamento.erros[0])
        self.assertEqual(session.commits, 1)

    def test_resultado_e_serializavel_para_a_rotina_26(self) -> None:
        resultado = executar_importacao(
            _SessionFalsa(),
            [DepartamentoImportacao("CIC", "DEPTO CIENCIAS DA COMPUTACAO")],
            ano="2026",
            periodo="2",
            coletor=lambda *_: ([], 0),
        ).to_dict()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["departamentos"][0]["erros"], [])
        self.assertIn("inicio", resultado)
        self.assertIn("fim", resultado)

    @patch("app.services.sigaa_import_service.salvar_oferta")
    def test_divergencia_do_total_e_reportada(self, salvar: Mock) -> None:
        resultado = executar_importacao(
            _SessionFalsa(),
            [DepartamentoImportacao("CIC", "DEPTO CIENCIAS DA COMPUTACAO")],
            ano="2026",
            periodo="2",
            coletor=lambda *_: ([_oferta("PROFESSORA TESTE")], 2),
        )

        departamento = resultado.departamentos[0]
        self.assertFalse(departamento.sucesso)
        self.assertIn("diverge", departamento.erros[0])
        self.assertEqual(departamento.ofertas_processadas, 1)

    @patch("app.services.sigaa_import_service.salvar_oferta")
    def test_falha_de_commit_e_reportada_e_reverte_contagem(
        self, salvar: Mock
    ) -> None:
        session = _SessionFalsa(RuntimeError("banco indisponivel"))
        resultado = executar_importacao(
            session,
            [DepartamentoImportacao("CIC", "DEPTO CIENCIAS DA COMPUTACAO")],
            ano="2026",
            periodo="2",
            coletor=lambda *_: ([_oferta("PROFESSORA TESTE")], 1),
        )

        departamento = resultado.departamentos[0]
        self.assertFalse(departamento.sucesso)
        self.assertEqual(departamento.ofertas_processadas, 0)
        self.assertIn("banco indisponivel", departamento.erros[0])
        self.assertEqual(session.rollbacks, 1)

    @patch("app.services.sigaa_import_service.salvar_oferta")
    def test_falha_de_rollback_tambem_e_reportada(self, salvar: Mock) -> None:
        session = _SessionFalsa(
            erro_commit=RuntimeError("commit falhou"),
            erro_rollback=RuntimeError("rollback falhou"),
        )
        resultado = executar_importacao(
            session,
            [DepartamentoImportacao("CIC", "DEPTO CIENCIAS DA COMPUTACAO")],
            ano="2026",
            periodo="2",
            coletor=lambda *_: ([_oferta("PROFESSORA TESTE")], 1),
        )

        erros = resultado.departamentos[0].erros
        self.assertEqual(len(erros), 2)
        self.assertIn("commit falhou", erros[0])
        self.assertIn("rollback falhou", erros[1])

    def test_exige_ao_menos_um_departamento(self) -> None:
        with self.assertRaisesRegex(ValueError, "ao menos um departamento"):
            executar_importacao(
                _SessionFalsa(),
                [],
                ano="2026",
                periodo="2",
                coletor=lambda *_: ([], 0),
            )


if __name__ == "__main__":
    unittest.main()
