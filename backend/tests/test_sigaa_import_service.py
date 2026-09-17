import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from app.scrapers.sigaa_poc import Oferta
from app.services.sigaa_import_service import (
    OfertaNaoPersistivelError,
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


if __name__ == "__main__":
    unittest.main()
