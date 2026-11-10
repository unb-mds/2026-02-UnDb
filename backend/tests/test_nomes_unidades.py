import asyncio
import json
import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.disciplina import Disciplina
from app.models.unidade import Unidade
from app.scrapers.sigaa_poc import Oferta
from app.services.sigaa_import_service import salvar_oferta


class NomesUnidadesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        turma = salvar_oferta(
            self.db,
            Oferta("FCE0001", "Disciplina", "01", "2026.2", ("Docente",), "100", "672"),
            "672",
            "FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM SAÚDE",
        )
        self.disciplina_id = turma.disciplina.id
        self.professor_id = turma.professores[0].id
        self.db.commit()
        self.db.expunge_all()
        app.dependency_overrides[get_db] = lambda: self.db

    def tearDown(self) -> None:
        app.dependency_overrides.pop(get_db, None)
        self.db.close()
        self.engine.dispose()

    @staticmethod
    def _get(path: str):
        from types import SimpleNamespace
        from urllib.parse import urlsplit

        async def request():
            url = urlsplit(path)
            messages = []
            received = False

            async def receive():
                nonlocal received
                if received:
                    return {"type": "http.disconnect"}
                received = True
                return {"type": "http.request", "body": b"", "more_body": False}

            async def send(message):
                messages.append(message)

            await app(
                {
                    "type": "http",
                    "asgi": {"version": "3.0"},
                    "http_version": "1.1",
                    "method": "GET",
                    "scheme": "http",
                    "path": url.path,
                    "raw_path": url.path.encode("ascii"),
                    "query_string": url.query.encode("ascii"),
                    "headers": [],
                    "client": ("127.0.0.1", 12345),
                    "server": ("testserver", 80),
                    "root_path": "",
                    "state": {},
                },
                receive,
                send,
            )
            status = next(m["status"] for m in messages if m["type"] == "http.response.start")
            body = b"".join(
                m.get("body", b"") for m in messages if m["type"] == "http.response.body"
            )
            return SimpleNamespace(status_code=status, json=lambda: json.loads(body))

        return asyncio.run(request())

    def test_nome_institucional_preserva_codigo_em_todos_os_contextos_publicos(self) -> None:
        disciplina = str(self.disciplina_id)
        professor = str(self.professor_id)
        for path in [
            "/api/disciplinas",
            f"/api/disciplinas/{disciplina}",
            "/api/professores",
            f"/api/professores/{professor}",
            f"/api/professores/{professor}/disciplinas",
        ]:
            with self.subTest(path=path):
                response = self._get(path)
                self.assertEqual(response.status_code, 200)
                value = response.json()
                item = value[0] if isinstance(value, list) else value
                self.assertEqual(item["departamento"], "672")
                self.assertEqual(
                    item["departamento_nome"], "FACULDADE DE CIÊNCIAS E TECNOLOGIAS EM SAÚDE"
                )
        aggregate = self._get(f"/api/professores/{professor}/disciplinas/{disciplina}").json()
        comparison = self._get(
            f"/api/disciplinas/{disciplina}/professores?ordenar_por=recomendacao"
        ).json()
        self.assertEqual(
            aggregate["disciplina"]["departamento_nome"],
            comparison["disciplina"]["departamento_nome"],
        )
        self.assertEqual(
            aggregate["professor"]["departamento_nome"],
            aggregate["disciplina"]["departamento_nome"],
        )
        turmas = self._get(f"/api/disciplinas/{disciplina}/turmas").json()
        self.assertEqual(
            turmas[0]["professores"][0]["departamento_nome"],
            aggregate["professor"]["departamento_nome"],
        )

    def test_nome_de_outra_fonte_nao_substitui_identidade_sigaa(self) -> None:
        self.db.add(Unidade(fonte="OUTRA", codigo="672", nome="Outra unidade"))
        self.db.commit()
        item = self._get(f"/api/disciplinas/{self.disciplina_id}").json()
        self.assertNotEqual(item["departamento_nome"], "Outra unidade")

    def test_registro_sem_unidade_permanece_acessivel_sem_inventar_nome(self) -> None:
        disciplina = Disciplina(codigo="SEM001", nome="Legado", departamento="999999")
        self.db.add(disciplina)
        self.db.commit()
        response = self._get(f"/api/disciplinas/{disciplina.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["departamento"], "999999")
        self.assertIsNone(response.json()["departamento_nome"])

    def test_lista_resolve_nomes_na_mesma_consulta_sem_n_mais_um(self) -> None:
        self.db.add_all(
            [
                Disciplina(codigo=f"FCE{i:04}", nome=f"Disciplina {i}", departamento="672")
                for i in range(2, 22)
            ]
        )
        self.db.commit()
        self.db.expunge_all()
        consultas = []

        def registrar(_conn, _cursor, statement, _parameters, _context, _executemany):
            consultas.append(statement)

        event.listen(self.engine, "before_cursor_execute", registrar)
        try:
            response = self._get("/api/disciplinas")
        finally:
            event.remove(self.engine, "before_cursor_execute", registrar)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 21)
        self.assertEqual(len(consultas), 1)


if __name__ == "__main__":
    unittest.main()
