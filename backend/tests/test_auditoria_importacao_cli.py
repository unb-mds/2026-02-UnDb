import contextlib
import io
import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.commands import auditar_importacao_sigaa, importar_sigaa_agendado
from app.core.database import Base
from app.models import ImportacaoExecucao


class AuditoriaImportacaoCliTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.saida = Path(self.directory.name) / "auditoria.json"
        self.id = uuid4()
        self.dados = {
            "id": self.id,
            "status": "sucesso",
            "ano": "2026",
            "periodo": "2",
            "iniciada_em": datetime.now(UTC),
            "finalizada_em": datetime.now(UTC),
            "ofertas_extraidas": 0,
            "ofertas_processadas": 0,
            "erro": None,
            "departamentos": [{"departamento": "CIC", "unidade_sigaa": "Computacao"}],
            "resultado_json": {
                "sucesso": True,
                "ano": "2026",
                "periodo": "2",
                "origem_unidades": "formulario_sigaa",
                "departamentos": [
                    {
                        "departamento": "CIC",
                        "sucesso": True,
                        "erros": [],
                        "ofertas_extraidas": 0,
                        "ofertas_processadas": 0,
                        "total_reportado": 0,
                    }
                ],
            },
        }

    def test_audita_id_explicito_sem_alterar_historico(self):
        with Session(self.engine) as db:
            db.add(ImportacaoExecucao(**self.dados))
            db.commit()
        with (
            patch.object(auditar_importacao_sigaa, "SessionLocal", lambda: Session(self.engine)),
            patch("sys.argv", ["auditar", "--execucao", str(self.id), "--saida", str(self.saida)]),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            with self.assertRaises(SystemExit) as result:
                auditar_importacao_sigaa.main()
        self.assertEqual(result.exception.code, 0)
        self.assertTrue(json.loads(self.saida.read_text())["cobertura_formulario_verificada"])
        with Session(self.engine) as db:
            self.assertEqual(
                db.get(ImportacaoExecucao, self.id).resultado_json, self.dados["resultado_json"]
            )

    def test_id_ausente_nao_audita_outra_execucao(self):
        with (
            patch.object(auditar_importacao_sigaa, "SessionLocal", lambda: Session(self.engine)),
            patch("sys.argv", ["auditar", "--execucao", str(self.id)]),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            with self.assertRaises(SystemExit) as result:
                auditar_importacao_sigaa.main()
        self.assertEqual(result.exception.code, 2)

    def test_importador_grava_auditoria_e_falha_quando_resumo_oculta_ausencia(self):
        self.dados["resultado_json"]["departamentos"] = []
        registro = SimpleNamespace(**self.dados)
        with (
            patch.object(importar_sigaa_agendado, "SessionLocal", lambda: Session(self.engine)),
            patch.object(
                importar_sigaa_agendado, "executar_importacao_agendada", return_value=registro
            ) as executar,
            patch(
                "sys.argv",
                [
                    "importar",
                    "--todas-unidades",
                    "--ano",
                    "2026",
                    "--periodo",
                    "2",
                    "--auditoria",
                    str(self.saida),
                ],
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            with self.assertRaises(SystemExit) as result:
                importar_sigaa_agendado.main()
        self.assertEqual(result.exception.code, 1)
        self.assertEqual(executar.call_args.kwargs["origem_unidades"], "formulario_sigaa")
        self.assertEqual(json.loads(self.saida.read_text())["ausentes"], ["CIC"])
