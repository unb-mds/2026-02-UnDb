"""Rehearsal HTTP/CLI exclusivo do PostgreSQL descartável undb_207_test."""

import json
import os
import subprocess
import sys
import socket
import time
from http.cookiejar import CookieJar
from urllib.error import URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener

from tests.test_reconciliacao_professores import ReconciliacaoTest
from app.core.security import gerar_hash_senha


def main():
    url = os.environ.get("RECONCILIACAO_POSTGRES_TEST_URL")
    if not url or url != os.environ.get("DATABASE_URL"):
        raise RuntimeError(
            "Definir ambas as URLs para o mesmo PostgreSQL descartável undb_207_test."
        )
    with socket.socket() as reserva:
        reserva.bind(("127.0.0.1", 8127))
    fixture = ReconciliacaoTest()
    fixture.setUp()  # Valida o nome do banco antes de qualquer escrita.
    processo = None
    cliente = build_opener(HTTPCookieProcessor(CookieJar()))

    def requisitar(path, body=None):
        if processo is not None and processo.poll() is not None:
            raise RuntimeError("Servidor de teste encerrou; não acessar outro serviço na porta.")
        request = Request(
            "http://127.0.0.1:8127" + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with cliente.open(request, timeout=5) as response:
            return json.load(response)

    try:
        avaliacao = fixture.avaliar(fixture.origem)
        usuario = avaliacao.usuario
        usuario.email_confirmado = True
        usuario.password_hash = gerar_hash_senha("SenhaFixture207!")
        fixture.db.commit()
        origem, destino = str(fixture.origem.id), str(fixture.destino.id)
        disciplina = str(fixture.t1.disciplina_id)
        command = [
            sys.executable,
            "-m",
            "app.commands.reconciliar_professores",
            "--origem",
            origem,
            "--destino",
            destino,
        ]
        previa = subprocess.run(command, check=True, capture_output=True, text=True)
        assert json.loads(previa.stdout)["estado"] == "pronta_para_confirmacao"
        aplicar = command + [
            "--aplicar",
            "--confirmo-mesma-pessoa",
            "--evidencia",
            "Fixture explícita de teste #207",
        ]
        subprocess.run(aplicar, check=True, capture_output=True)
        repetida = subprocess.run(aplicar, check=True, capture_output=True, text=True)
        assert json.loads(repetida.stdout)["estado"] == "ja_aplicada"
        # Nenhuma sessão anterior à manutenção fica escrevendo depois dela.
        email = usuario.email
        avaliacao_id = str(avaliacao.id)
        fixture.db.close()
        processo = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8127",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ, "DEBUG": "True"},  # Cookie HTTP somente nesta fixture local.
        )
        for _ in range(50):
            try:
                requisitar("/health")
                break
            except URLError:
                time.sleep(0.1)
        else:
            raise RuntimeError("API de teste não iniciou; verificar porta 8127 livre.")
        assert len(requisitar("/api/professores?nome=DOCENTE")) == 1
        assert requisitar(f"/api/professores/{origem}")["id"] == destino
        consulta = requisitar(f"/api/professores/{origem}/disciplinas/{disciplina}")
        assert consulta["total_avaliacoes"] == 1 and not consulta["dados_suficientes"]
        requisitar("/api/auth/login", {"email": email, "senha": "SenhaFixture207!"})
        envio = requisitar(
            "/api/avaliacoes",
            {
                "professor_id": origem,
                "disciplina_id": disciplina,
                "didatica": 5,
                "dificuldade": "MEDIO",
                "chamada": True,
                "disponibiliza_material": False,
                "recomenda": True,
            },
        )
        assert envio["id"] == avaliacao_id, "ID antigo deve substituir a mesma avaliação."
        assert (
            requisitar(f"/api/professores/{destino}/disciplinas/{disciplina}")["total_avaliacoes"]
            == 1
        )
        print(
            "HTTP/CLI PostgreSQL: simulação, aplicação, repetição, busca única, ID antigo, privacidade, login e substituição sem duplicar aprovados."
        )
    finally:
        if processo is not None:
            processo.terminate()
            processo.wait(timeout=10)
        fixture.tearDown()


if __name__ == "__main__":
    main()
