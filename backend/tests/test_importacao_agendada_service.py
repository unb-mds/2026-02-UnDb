import unittest
from datetime import UTC, datetime
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.commands.importar_sigaa_agendado import _todas_unidades
from app.models import ImportacaoExecucao, Unidade  # noqa: F401
from app.services.importacao_agendada_service import executar_importacao_agendada
from app.services.sigaa_import_service import (
    DepartamentoImportacao,
    ResultadoDepartamento,
    ResultadoImportacao,
)


def _resultado(*, sucesso: bool, erros: tuple[str, ...] = ()) -> ResultadoImportacao:
    agora = datetime.now(UTC)
    departamento = ResultadoDepartamento(
        departamento="CIC",
        unidade_sigaa="DEPTO CIÊNCIAS DA COMPUTAÇÃO",
        sucesso=sucesso,
        total_reportado=2,
        ofertas_extraidas=2,
        ofertas_processadas=2 if sucesso else 1,
        erros=erros,
    )
    return ResultadoImportacao(
        sucesso=sucesso,
        ano="2026",
        periodo="2",
        inicio=agora,
        fim=agora,
        departamentos=(departamento,),
    )


class ImportacaoAgendadaServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.departamentos = [
            DepartamentoImportacao("CIC", "DEPTO CIÊNCIAS DA COMPUTAÇÃO")
        ]

    def tearDown(self) -> None:
        self.engine.dispose()

    @patch("app.services.importacao_agendada_service.executar_importacao")
    def test_registra_execucao_com_sucesso(self, executar_importacao) -> None:
        executar_importacao.return_value = _resultado(sucesso=True)

        with Session(self.engine) as db:
            registro = executar_importacao_agendada(
                db,
                self.departamentos,
                ano="2026",
                periodo="2",
            )
            registro_id = registro.id

        with Session(self.engine) as db:
            persistido = db.scalar(
                select(ImportacaoExecucao).where(
                    ImportacaoExecucao.id == registro_id
                )
            )
            self.assertIsNotNone(persistido)
            self.assertEqual(persistido.status, "sucesso")
            self.assertEqual(persistido.ofertas_extraidas, 2)
            self.assertEqual(persistido.ofertas_processadas, 2)
            self.assertIsNone(persistido.erro)
            self.assertIsNotNone(persistido.finalizada_em)

    @patch("app.services.importacao_agendada_service.executar_importacao")
    def test_registra_falha_retornada_pela_importacao(
        self, executar_importacao
    ) -> None:
        executar_importacao.return_value = _resultado(
            sucesso=False,
            erros=("SIGAA indisponível",),
        )

        with Session(self.engine) as db:
            registro = executar_importacao_agendada(
                db,
                self.departamentos,
                ano="2026",
                periodo="2",
            )
            self.assertEqual(registro.status, "falha")
            self.assertEqual(registro.ofertas_extraidas, 2)
            self.assertEqual(registro.ofertas_processadas, 1)
            self.assertEqual(registro.erro, "SIGAA indisponível")
            self.assertFalse(registro.resultado_json["sucesso"])

    @patch("app.services.importacao_agendada_service.executar_importacao")
    def test_registra_excecao_inesperada(self, executar_importacao) -> None:
        executar_importacao.side_effect = RuntimeError("falha inesperada")

        with Session(self.engine) as db:
            registro = executar_importacao_agendada(
                db,
                self.departamentos,
                ano="2026",
                periodo="2",
            )
            registro_id = registro.id

        with Session(self.engine) as db:
            persistido = db.scalar(
                select(ImportacaoExecucao).where(
                    ImportacaoExecucao.id == registro_id
                )
            )
            self.assertEqual(persistido.status, "falha")
            self.assertIn("RuntimeError: falha inesperada", persistido.erro)
            self.assertFalse(persistido.resultado_json["sucesso"])

    def test_registra_falha_ao_enumerar_unidades(self) -> None:
        def enumerar():
            raise RuntimeError("formulário SIGAA indisponível")

        with Session(self.engine) as db:
            registro = executar_importacao_agendada(
                db, enumerar, ano="2026", periodo="2"
            )
            registro_id = registro.id

        with Session(self.engine) as db:
            persistido = db.get(ImportacaoExecucao, registro_id)
            self.assertEqual(persistido.status, "falha")
            self.assertIn("formulário SIGAA indisponível", persistido.erro)
            self.assertEqual(persistido.departamentos, [])

    @patch("app.commands.importar_sigaa_agendado.listar_unidades_reais")
    def test_enumeracao_reutiliza_codigo_de_unidade_existente(self, listar) -> None:
        listar.return_value = [
            ("508", "DEPTO CIÊNCIAS DA COMPUTAÇÃO"),
            ("672", "CAMPUS CEILÂNDIA"),
        ]
        with Session(self.engine) as db:
            db.add(Unidade(
                fonte="SIGAA", codigo="CIC", nome="CIC", identificador_externo="508"
            ))
            db.commit()
            solicitacoes = _todas_unidades(db)

        self.assertEqual(
            [(item.departamento, item.unidade_sigaa) for item in solicitacoes],
            [("CIC", "DEPTO CIÊNCIAS DA COMPUTAÇÃO"), ("672", "CAMPUS CEILÂNDIA")],
        )


if __name__ == "__main__":
    unittest.main()
