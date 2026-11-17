"""Regressões do preflight da #267 sem acessar o daemon Docker."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import recovery_drill as drill


class DockerEndpointTests(unittest.TestCase):
    def preflight(self, environment, endpoint):
        calls = []

        def execute(command, **kwargs):
            calls.append((command, kwargs["env"]))
            if command[0] == "git":
                output = "synthetic-sha"
            elif command[1:3] == ("context", "show"):
                output = "selected-context"
            elif command[1:3] == ("context", "inspect"):
                output = endpoint
            else:
                # Interrompe antes de criar recursos ou acessar um daemon.
                return subprocess.CompletedProcess(command, 1, "")
            return subprocess.CompletedProcess(command, 0, output)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with (
                patch.dict(drill.os.environ, environment, clear=True),
                patch.object(
                    drill.sys,
                    "argv",
                    [
                        "recovery_drill.py",
                        "--confirm-disposable",
                        "--image",
                        "synthetic",
                        "--output",
                        str(output),
                    ],
                ),
                patch.object(drill.subprocess, "run", side_effect=execute),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(drill.main(), 1)
            result = json.loads(output.read_text())
        return calls, result

    def test_remote_context_overrides_local_host_and_is_refused(self):
        calls, result = self.preflight(
            {"DOCKER_CONTEXT": "remote", "DOCKER_HOST": "unix:///local.sock"},
            "ssh://remote.example",
        )
        self.assertEqual(len(calls), 3)
        self.assertNotIn("docker_contexto_local", result)
        self.assertIn("sem endpoint remoto", result["falha"]["detalhe"])

    def test_local_context_overrides_remote_host(self):
        self.assert_pinned(
            {"DOCKER_CONTEXT": "local", "DOCKER_HOST": "tcp://remote.example:2375"},
            "unix:///context.sock",
            "unix:///context.sock",
        )

    def test_host_without_context(self):
        self.assert_pinned(
            {"DOCKER_HOST": "unix:///host.sock"},
            "unix:///default.sock",
            "unix:///host.sock",
        )

    def test_default_context(self):
        endpoint = "npipe:////./pipe/docker_engine"
        self.assert_pinned({}, endpoint, endpoint)

    def assert_pinned(self, environment, endpoint, expected):
        calls, result = self.preflight(environment, endpoint)
        command, child_env = calls[-1]
        self.assertEqual(command[:4], ("docker", "--host", expected, "version"))
        self.assertNotIn("DOCKER_CONTEXT", child_env)
        self.assertNotIn("DOCKER_HOST", child_env)
        self.assertTrue(result["docker_contexto_local"])


if __name__ == "__main__":
    unittest.main()
