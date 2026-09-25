import asyncio
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, UniqueConstraint, create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://teste:teste@localhost:5432/teste",
)
os.environ.setdefault("SECRET_KEY", "teste-local")

from app.core.database import Base
from app.core.auth import SESSION_COOKIE_NAME
from app.core.database import get_db
from app.core.security import gerar_hash_token
from app.main import app
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.enums import Dificuldade, QualidadeMaterial
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.turma import Turma
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from app.routers import avaliacoes as avaliacoes_router
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoResponse
from app.services import avaliacao_service


class AvaliacaoSchemaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "professor_id": str(uuid4()),
            "disciplina_id": str(uuid4()),
            "didatica": 3,
            "dificuldade": "MEDIO",
            "chamada": True,
            "disponibiliza_material": True,
            "qualidade_material": "BOM",
            "recomenda": True,
        }

    def test_aceita_todas_as_escalas_definidas(self) -> None:
        for didatica in (1, 5):
            for dificuldade in Dificuldade:
                with self.subTest(didatica=didatica, dificuldade=dificuldade):
                    avaliacao = AvaliacaoCreate.model_validate(
                        {
                            **self.payload,
                            "didatica": didatica,
                            "dificuldade": dificuldade.value,
                        }
                    )
                    self.assertEqual(avaliacao.didatica, didatica)
                    self.assertEqual(avaliacao.dificuldade, dificuldade)

        for qualidade in QualidadeMaterial:
            with self.subTest(qualidade=qualidade):
                avaliacao = AvaliacaoCreate.model_validate(
                    {**self.payload, "qualidade_material": qualidade.value}
                )
                self.assertEqual(avaliacao.qualidade_material, qualidade)

        payload_sem_material = {
            **self.payload,
            "disponibiliza_material": False,
        }
        payload_sem_material.pop("qualidade_material")
        sem_material = AvaliacaoCreate.model_validate(payload_sem_material)
        self.assertIsNone(sem_material.qualidade_material)

    def test_rejeita_didatica_fora_da_escala_ou_nao_inteira(self) -> None:
        for valor in (0, 6, "3", 3.0, True):
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                AvaliacaoCreate.model_validate({**self.payload, "didatica": valor})

    def test_rejeita_valores_fora_dos_enums(self) -> None:
        for campo, valor in (
            ("dificuldade", "CONFLITANTE"),
            ("dificuldade", "MUITO_DIFICIL"),
            ("qualidade_material", "EXCELENTE"),
            ("qualidade_material", "NAO_DISPONIBILIZA"),
        ):
            with self.subTest(campo=campo, valor=valor), self.assertRaises(ValidationError):
                AvaliacaoCreate.model_validate({**self.payload, campo: valor})

    def test_rejeita_coercao_de_campos_booleanos(self) -> None:
        for campo in ("chamada", "disponibiliza_material", "recomenda"):
            for valor in (0, 1, "sim", "nao", "true", "false"):
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValidationError):
                    AvaliacaoCreate.model_validate({**self.payload, campo: valor})

    def test_exige_qualidade_apenas_quando_material_e_disponibilizado(self) -> None:
        casos_invalidos = (
            {**self.payload, "qualidade_material": None},
            {
                **self.payload,
                "disponibiliza_material": False,
                "qualidade_material": "RUIM",
            },
        )

        for payload in casos_invalidos:
            with self.subTest(payload=payload), self.assertRaisesRegex(
                ValidationError,
                "qualidade_material e obrigatoria",
            ):
                AvaliacaoCreate.model_validate(payload)

    def test_rejeita_campos_fora_do_formulario_da_release_1(self) -> None:
        for campo in ("comentario", "nota_geral", "usuario_id", "created_at"):
            with self.subTest(campo=campo), self.assertRaises(ValidationError):
                AvaliacaoCreate.model_validate({**self.payload, campo: "nao permitido"})


class AvaliacaoModelTest(unittest.TestCase):
    def test_modelo_contem_identificacao_criterios_e_datas(self) -> None:
        self.assertEqual(
            set(Avaliacao.__table__.columns.keys()),
            {
                "id",
                "usuario_id",
                "professor_id",
                "disciplina_id",
                "didatica",
                "dificuldade",
                "chamada",
                "disponibiliza_material",
                "qualidade_material",
                "recomenda",
                "created_at",
                "updated_at",
            },
        )

        for coluna in (
            "usuario_id",
            "professor_id",
            "disciplina_id",
            "didatica",
            "dificuldade",
            "chamada",
            "disponibiliza_material",
            "recomenda",
            "created_at",
            "updated_at",
        ):
            with self.subTest(coluna=coluna):
                self.assertFalse(Avaliacao.__table__.columns[coluna].nullable)

    def test_modelo_garante_unicidade_por_usuario_professor_disciplina(self) -> None:
        constraint = next(
            item
            for item in Avaliacao.__table__.constraints
            if isinstance(item, UniqueConstraint)
            and item.name == "uq_avaliacao_usuario_professor_disciplina"
        )

        self.assertEqual(
            tuple(coluna.name for coluna in constraint.columns),
            ("usuario_id", "professor_id", "disciplina_id"),
        )

    def test_modelo_materializa_regras_de_escala_e_material(self) -> None:
        checks = {
            item.name: str(item.sqltext)
            for item in Avaliacao.__table__.constraints
            if isinstance(item, CheckConstraint)
        }

        self.assertEqual(checks["ck_avaliacao_didatica"], "didatica BETWEEN 1 AND 5")
        self.assertIn("qualidade_material IS NOT NULL", checks["ck_avaliacao_qualidade_material"])
        self.assertIn("qualidade_material IS NULL", checks["ck_avaliacao_qualidade_material"])

    def test_modelo_referencia_usuario_professor_e_disciplina(self) -> None:
        referencias = {
            coluna.name: next(iter(coluna.foreign_keys)).target_fullname
            for coluna in (
                Avaliacao.__table__.columns.usuario_id,
                Avaliacao.__table__.columns.professor_id,
                Avaliacao.__table__.columns.disciplina_id,
            )
        }

        self.assertEqual(
            referencias,
            {
                "usuario_id": "usuarios.id",
                "professor_id": "professores.id",
                "disciplina_id": "disciplinas.id",
            },
        )


class RegistroAvaliacaoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.usuario = Usuario(
            nome="Maria",
            email="maria@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=True,
        )
        self.professor = Professor(nome="Professora Teste", departamento="CIC")
        self.disciplina = Disciplina(
            codigo="CIC0001",
            nome="Disciplina Teste",
            departamento="CIC",
        )
        self.unidade = Unidade(codigo="CIC", nome="CIC")
        self.db.add_all((self.usuario, self.professor, self.disciplina, self.unidade))
        self.db.flush()
        self.db.add(Turma(
            disciplina=self.disciplina,
            unidade=self.unidade,
            codigo="01",
            semestre="2026.2",
            professores=[self.professor],
        ))
        self.db.commit()
        self.dados = AvaliacaoCreate(
            professor_id=self.professor.id,
            disciplina_id=self.disciplina.id,
            didatica=4,
            dificuldade="MEDIO",
            chamada=True,
            disponibiliza_material=True,
            qualidade_material="BOM",
            recomenda=True,
        )

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_envio_valido_persiste_avaliador_e_retorna_schema(self) -> None:
        resposta = avaliacoes_router.registrar_avaliacao(
            self.dados,
            self.usuario,
            self.db,
        )

        registro = self.db.scalar(select(Avaliacao))
        self.assertIsInstance(resposta, AvaliacaoResponse)
        self.assertEqual(registro.usuario_id, self.usuario.id)
        self.assertEqual(resposta.id, registro.id)
        self.assertNotIn("usuario_id", resposta.model_dump())
        self.assertIsNotNone(resposta.created_at)
        self.assertIsNotNone(resposta.updated_at)

    def test_novo_envio_substitui_sem_duplicar_e_atualiza_updated_at(self) -> None:
        primeira = avaliacao_service.registrar_avaliacao(
            self.db,
            self.usuario,
            self.dados,
        )
        id_original = primeira.id
        created_at_original = primeira.created_at
        instante_antigo = datetime(2000, 1, 1, tzinfo=timezone.utc)
        primeira.updated_at = instante_antigo
        self.db.commit()

        substituida = avaliacao_service.registrar_avaliacao(
            self.db,
            self.usuario,
            self.dados.model_copy(
                update={
                    "didatica": 1,
                    "dificuldade": Dificuldade.DIFICIL,
                    "chamada": False,
                    "disponibiliza_material": False,
                    "qualidade_material": None,
                    "recomenda": False,
                }
            ),
        )

        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual(quantidade, 1)
        self.assertEqual(substituida.id, id_original)
        self.assertEqual(substituida.created_at, created_at_original)
        self.assertNotEqual(substituida.updated_at, instante_antigo)
        self.assertEqual(substituida.didatica, 1)
        self.assertFalse(substituida.disponibiliza_material)
        self.assertIsNone(substituida.qualidade_material)

    def test_usuarios_e_pares_distintos_nao_se_substituem(self) -> None:
        outro_usuario = Usuario(
            nome="Ana",
            email="ana@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=True,
        )
        outra_disciplina = Disciplina(
            codigo="CIC0002",
            nome="Outra Disciplina",
            departamento="CIC",
        )
        self.db.add_all((outro_usuario, outra_disciplina))
        self.db.add(Turma(
            disciplina=outra_disciplina,
            unidade=self.unidade,
            codigo="01",
            semestre="2026.2",
            professores=[self.professor],
        ))
        self.db.commit()

        primeira = avaliacao_service.registrar_avaliacao(
            self.db, self.usuario, self.dados
        )
        segundo_usuario = avaliacao_service.registrar_avaliacao(
            self.db, outro_usuario, self.dados
        )
        outro_par = avaliacao_service.registrar_avaliacao(
            self.db,
            self.usuario,
            self.dados.model_copy(update={"disciplina_id": outra_disciplina.id}),
        )

        registros = self.db.scalars(select(Avaliacao)).all()
        self.assertEqual(len(registros), 3)
        self.assertEqual(
            {registro.id for registro in registros},
            {primeira.id, segundo_usuario.id, outro_par.id},
        )
        self.assertEqual(
            {
                (registro.usuario_id, registro.professor_id, registro.disciplina_id)
                for registro in registros
            },
            {
                (self.usuario.id, self.professor.id, self.disciplina.id),
                (outro_usuario.id, self.professor.id, self.disciplina.id),
                (self.usuario.id, self.professor.id, outra_disciplina.id),
            },
        )

    def test_rejeita_professor_ou_disciplina_inexistente_sem_persistir(self) -> None:
        casos = (
            ("professor", self.dados.model_copy(update={"professor_id": uuid4()})),
            ("disciplina", self.dados.model_copy(update={"disciplina_id": uuid4()})),
        )
        for recurso, dados in casos:
            with self.subTest(recurso=recurso), self.assertRaisesRegex(
                avaliacao_service.RecursoNaoEncontradoError,
                recurso,
            ):
                avaliacao_service.registrar_avaliacao(self.db, self.usuario, dados)

        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual(quantidade, 0)

    def test_rejeita_par_sem_vinculo_sem_persistir(self) -> None:
        outro_professor = Professor(nome="Professor sem vínculo", departamento="CIC")
        self.db.add(outro_professor)
        self.db.commit()

        with self.assertRaisesRegex(
            avaliacao_service.RecursoNaoEncontradoError, "vinculo"
        ):
            avaliacao_service.registrar_avaliacao(
                self.db,
                self.usuario,
                self.dados.model_copy(update={"professor_id": outro_professor.id}),
            )

        self.assertEqual(self.db.scalar(select(func.count()).select_from(Avaliacao)), 0)

    def test_router_traduz_referencia_inexistente_para_404(self) -> None:
        with self.assertRaises(HTTPException) as contexto:
            avaliacoes_router.registrar_avaliacao(
                self.dados.model_copy(update={"professor_id": uuid4()}),
                self.usuario,
                self.db,
            )

        self.assertEqual(contexto.exception.status_code, 404)

    def test_contrato_post_avaliacoes_esta_no_openapi(self) -> None:
        operacoes = app.openapi()["paths"]["/api/avaliacoes"]
        rota = avaliacoes_router.router.routes[0]

        self.assertIn("post", operacoes)
        self.assertIn(
            "obter_usuario_confirmado",
            {dependencia.call.__name__ for dependencia in rota.dependant.dependencies},
        )
        self.assertEqual(
            operacoes["post"]["responses"]["200"]["content"]["application/json"][
                "schema"
            ]["$ref"],
            "#/components/schemas/AvaliacaoResponse",
        )


class RegistroAvaliacaoHttpTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.usuario_confirmado = Usuario(
            nome="Maria",
            email="maria.http@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=True,
        )
        self.usuario_nao_confirmado = Usuario(
            nome="Ana",
            email="ana.http@aluno.unb.br",
            password_hash="hash-de-teste",
            email_confirmado=False,
        )
        self.professor = Professor(nome="Professora HTTP", departamento="CIC")
        self.disciplina = Disciplina(
            codigo="CIC0099",
            nome="Disciplina HTTP",
            departamento="CIC",
        )
        self.unidade = Unidade(codigo="CIC", nome="CIC")
        self.db.add_all(
            (
                self.usuario_confirmado,
                self.usuario_nao_confirmado,
                self.professor,
                self.disciplina,
                self.unidade,
            )
        )
        self.db.flush()
        self.db.add(Turma(
            disciplina=self.disciplina,
            unidade=self.unidade,
            codigo="01",
            semestre="2026.2",
            professores=[self.professor],
        ))
        self.token_confirmado = "token-confirmado"
        self.token_nao_confirmado = "token-nao-confirmado"
        expiracao = datetime.now(timezone.utc) + timedelta(days=1)
        self.db.add_all(
            (
                SessaoUsuario(
                    usuario_id=self.usuario_confirmado.id,
                    token_hash=gerar_hash_token(self.token_confirmado),
                    expires_at=expiracao,
                ),
                SessaoUsuario(
                    usuario_id=self.usuario_nao_confirmado.id,
                    token_hash=gerar_hash_token(self.token_nao_confirmado),
                    expires_at=expiracao,
                ),
            )
        )
        self.db.commit()
        self.payload = {
            "professor_id": str(self.professor.id),
            "disciplina_id": str(self.disciplina.id),
            "didatica": 4,
            "dificuldade": "MEDIO",
            "chamada": True,
            "disponibiliza_material": True,
            "qualidade_material": "BOM",
            "recomenda": True,
        }

        def override_get_db():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db

    def tearDown(self) -> None:
        app.dependency_overrides.pop(get_db, None)
        self.db.close()
        self.engine.dispose()

    @staticmethod
    async def _request(
        payload: dict,
        token: str | None = None,
    ) -> tuple[int, dict]:
        corpo = json.dumps(payload).encode("utf-8")
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(corpo)).encode("ascii")),
        ]
        if token is not None:
            headers.append(
                (b"cookie", f"{SESSION_COOKIE_NAME}={token}".encode("ascii"))
            )

        recebido = False

        async def receive():
            nonlocal recebido
            if recebido:
                return {"type": "http.disconnect"}
            recebido = True
            return {"type": "http.request", "body": corpo, "more_body": False}

        mensagens = []

        async def send(message):
            mensagens.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/api/avaliacoes",
                "raw_path": b"/api/avaliacoes",
                "query_string": b"",
                "headers": headers,
                "client": ("127.0.0.1", 12345),
                "server": ("testserver", 80),
                "root_path": "",
                "state": {},
            },
            receive,
            send,
        )
        inicio = next(
            mensagem
            for mensagem in mensagens
            if mensagem["type"] == "http.response.start"
        )
        resposta = b"".join(
            mensagem.get("body", b"")
            for mensagem in mensagens
            if mensagem["type"] == "http.response.body"
        )
        return inicio["status"], json.loads(resposta)

    def test_http_exige_sessao_valida(self) -> None:
        for token in (None, "token-invalido"):
            with self.subTest(token=token):
                status_code, resposta = asyncio.run(self._request(self.payload, token))
                self.assertEqual(status_code, 401)
                self.assertIn("Sessão", resposta["detail"])

        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual(quantidade, 0)

    def test_http_bloqueia_email_nao_confirmado(self) -> None:
        status_code, resposta = asyncio.run(
            self._request(self.payload, self.token_nao_confirmado)
        )

        self.assertEqual(status_code, 403)
        self.assertIn("Confirme seu e-mail", resposta["detail"])
        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual(quantidade, 0)

    def test_http_persiste_usuario_confirmado_e_retorna_schema(self) -> None:
        status_code, resposta = asyncio.run(
            self._request(self.payload, self.token_confirmado)
        )

        self.db.expire_all()
        registro = self.db.scalar(select(Avaliacao))
        self.assertEqual(status_code, 200)
        self.assertEqual(registro.usuario_id, self.usuario_confirmado.id)
        self.assertEqual(resposta["id"], str(registro.id))
        self.assertNotIn("usuario_id", resposta)

    def test_http_rejeita_professor_sem_vinculo(self) -> None:
        outro_professor = Professor(nome="Professor sem vínculo", departamento="CIC")
        self.db.add(outro_professor)
        self.db.commit()

        status_code, resposta = asyncio.run(
            self._request(
                {**self.payload, "professor_id": str(outro_professor.id)},
                self.token_confirmado,
            )
        )

        self.assertEqual(status_code, 404)
        self.assertIn("vinculo", resposta["detail"])
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Avaliacao)), 0)

    def test_http_substitui_sem_duplicar_e_atualiza_updated_at(self) -> None:
        primeiro_status, primeira_resposta = asyncio.run(
            self._request(self.payload, self.token_confirmado)
        )
        registro = self.db.scalar(select(Avaliacao))
        instante_antigo = datetime(2000, 1, 1, tzinfo=timezone.utc)
        registro.updated_at = instante_antigo
        self.db.commit()

        segundo_status, segunda_resposta = asyncio.run(
            self._request(
                {
                    **self.payload,
                    "didatica": 1,
                    "dificuldade": "DIFICIL",
                    "chamada": False,
                    "disponibiliza_material": False,
                    "qualidade_material": None,
                    "recomenda": False,
                },
                self.token_confirmado,
            )
        )

        self.db.expire_all()
        substituida = self.db.scalar(select(Avaliacao))
        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual((primeiro_status, segundo_status), (200, 200))
        self.assertEqual(quantidade, 1)
        self.assertEqual(segunda_resposta["id"], primeira_resposta["id"])
        self.assertEqual(substituida.didatica, 1)
        self.assertNotEqual(substituida.updated_at, instante_antigo)

    def test_http_rejeita_comentario_sem_persistir(self) -> None:
        status_code, _ = asyncio.run(
            self._request(
                {**self.payload, "comentario": "campo livre proibido"},
                self.token_confirmado,
            )
        )

        self.assertEqual(status_code, 422)
        quantidade = self.db.scalar(select(func.count()).select_from(Avaliacao))
        self.assertEqual(quantidade, 0)


if __name__ == "__main__":
    unittest.main()
