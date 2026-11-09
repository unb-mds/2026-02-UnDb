import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.commands.iniciar_servidor import main


class InicializacaoTest(unittest.TestCase):
    def test_falha_de_migracao_impede_inicio_do_servidor(self):
        with (
            patch.dict(sys.modules, {"app.core.config": SimpleNamespace(PORT=10000)}),
            patch("app.commands.iniciar_servidor.subprocess.run") as migrate,
            patch("app.commands.iniciar_servidor.os.execv") as serve,
        ):
            migrate.side_effect = subprocess.CalledProcessError(1, "alembic")
            with self.assertRaises(subprocess.CalledProcessError):
                main()
            serve.assert_not_called()

    def test_migracao_antecede_servidor_com_porta_configurada(self):
        events = []
        with (
            patch.dict(sys.modules, {"app.core.config": SimpleNamespace(PORT=12345)}),
            patch("app.commands.iniciar_servidor.subprocess.run") as migrate,
            patch("app.commands.iniciar_servidor.os.execv") as serve,
        ):
            migrate.side_effect = lambda *a, **kw: events.append("migration")
            serve.side_effect = lambda *a: events.append("server")
            main()
            self.assertEqual(events, ["migration", "server"])
            migrate.assert_called_once_with(
                [sys.executable, "-m", "alembic", "upgrade", "head"], check=True
            )
            self.assertEqual(serve.call_args.args[1][-2:], ["--port", "12345"])

    def test_porta_invalida_nao_altera_banco(self):
        with (
            patch.dict(sys.modules, {"app.core.config": SimpleNamespace(PORT=0)}),
            patch("app.commands.iniciar_servidor.subprocess.run") as migrate,
        ):
            with self.assertRaises(ValueError):
                main()
            migrate.assert_not_called()
