"""Verifica o destino real do Alembic sem depender de PostgreSQL externo."""

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MigrationConnectionTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.runtime = Path(self.directory.name) / "runtime.db"
        # O caractere % também verifica o escape de interpolação do Alembic.
        self.migration = Path(self.directory.name) / "migration%170.db"
        self.environment = {
            **os.environ,
            "SECRET_KEY": "migration-test-only",
            "DATABASE_URL": f"sqlite+pysqlite:///{self.runtime.as_posix()}",
        }
        self.environment.pop("MIGRATION_DATABASE_URL", None)

    def migrate(self):
        return subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "20260911_01"],
            cwd=Path(__file__).resolve().parents[1],
            env=self.environment,
            capture_output=True,
            text=True,
        )

    def assert_migrated(self, path):
        self.assertTrue(path.exists())
        with sqlite3.connect(path) as connection:
            self.assertEqual(
                connection.execute("SELECT version_num FROM alembic_version").fetchone(),
                ("20260911_01",),
            )
            self.assertIsNotNone(
                connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'usuarios'"
                ).fetchone()
            )

    def test_explicit_migration_connection_does_not_migrate_runtime_database(self):
        self.environment["MIGRATION_DATABASE_URL"] = (
            f"sqlite+pysqlite:///{self.migration.as_posix().replace('%', '%25')}"
        )
        result = self.migrate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_migrated(self.migration)
        self.assertFalse(self.runtime.exists())

    def test_without_override_preserves_existing_database_url_behavior(self):
        result = self.migrate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_migrated(self.runtime)
        self.assertFalse(self.migration.exists())

    def test_invalid_override_fails_without_falling_back_to_runtime_database(self):
        self.environment["MIGRATION_DATABASE_URL"] = "invalid-connection"
        result = self.migrate()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.runtime.exists())
        self.assertFalse(self.migration.exists())
