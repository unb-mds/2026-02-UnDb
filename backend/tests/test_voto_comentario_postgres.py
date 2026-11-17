"""Concorrência e FKs reais. Exige banco descartável exclusivo migrado."""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models.avaliacao import Avaliacao
from app.models.comentario_versao import ComentarioVersao
from app.models.disciplina import Disciplina
from app.models.enums import EstadoComentario
from app.models.professor import Professor
from app.models.usuario import Usuario
from app.models.voto_comentario import VotoComentario
from app.services import voto_comentario_service as servico
from app.repositories import comentario_repository


@unittest.skipUnless(os.getenv("VOTOS_POSTGRES_TEST_URL"), "PostgreSQL exclusivo não configurado")
class VotoPostgresTest(unittest.TestCase):
    def setUp(self):
        url = make_url(os.environ["VOTOS_POSTGRES_TEST_URL"])
        if url.host not in ("localhost", "127.0.0.1") or url.database not in ("undb278_test", "ci"):
            raise ValueError("Use somente banco local descartável undb278_test ou ci")
        self.engine = create_engine(url)
        with Session(self.engine) as db:
            self.autor = Usuario(
                nome="Autor sintético",
                email=f"{uuid4()}@aluno.unb.br",
                password_hash="teste",
                email_confirmado=True,
            )
            self.eleitor = Usuario(
                nome="Conta sintética",
                email=f"{uuid4()}@aluno.unb.br",
                password_hash="teste",
                email_confirmado=True,
            )
            professor = Professor(nome="Professor sintético", departamento="TESTE")
            disciplina = Disciplina(
                nome="Disciplina sintética", codigo=str(uuid4())[:12], departamento="TESTE"
            )
            db.add_all([self.autor, self.eleitor, professor, disciplina])
            db.flush()
            avaliacao = Avaliacao(
                usuario_id=self.autor.id,
                professor_id=professor.id,
                disciplina_id=disciplina.id,
                didatica=4,
                dificuldade="MEDIO",
                chamada=True,
                disponibiliza_material=False,
                qualidade_material=None,
                recomenda=True,
            )
            db.add(avaliacao)
            db.flush()
            versao = ComentarioVersao(
                avaliacao_id=avaliacao.id,
                texto="Texto sintético",
                estado=EstadoComentario.PUBLICADO,
            )
            db.add(versao)
            db.flush()
            self.ids = (
                self.autor.id,
                self.eleitor.id,
                professor.id,
                disciplina.id,
                avaliacao.id,
                versao.id,
            )
            db.commit()

    def tearDown(self):
        autor, eleitor, professor, disciplina, avaliacao, versao = self.ids
        with Session(self.engine) as db:
            db.execute(delete(ComentarioVersao).where(ComentarioVersao.id == versao))
            db.execute(delete(Avaliacao).where(Avaliacao.id == avaliacao))
            db.execute(delete(Usuario).where(Usuario.id.in_([autor, eleitor])))
            db.execute(delete(Professor).where(Professor.id == professor))
            db.execute(delete(Disciplina).where(Disciplina.id == disciplina))
            db.commit()
        self.engine.dispose()

    def simultaneos(self, valores):
        barreira = Barrier(len(valores))

        def executar(voto):
            with Session(self.engine) as db:
                usuario = db.get(Usuario, self.ids[1])
                barreira.wait(timeout=10)
                return servico.definir(db, self.ids[5], usuario, voto)

        with ThreadPoolExecutor(max_workers=len(valores)) as pool:
            return list(pool.map(executar, valores))

    def test_concorrencia_upsert_troca_retirada(self):
        self.simultaneos(["UTIL", "UTIL"])
        with Session(self.engine) as db:
            self.assertEqual(
                db.scalar(
                    select(func.count())
                    .select_from(VotoComentario)
                    .where(VotoComentario.comentario_versao_id == self.ids[5])
                ),
                1,
            )
        self.simultaneos(["UTIL", "NAO_UTIL"])
        with Session(self.engine) as db:
            resumo = servico.consultar(db, self.ids[5], db.get(Usuario, self.ids[1]))
            self.assertEqual(resumo["uteis"] + resumo["nao_uteis"], 1)
        self.simultaneos([None, None])
        with Session(self.engine) as db:
            self.assertEqual(servico.consultar(db, self.ids[5], None)["uteis"], 0)
            self.assertEqual(
                db.scalar(
                    select(func.count())
                    .select_from(VotoComentario)
                    .where(VotoComentario.comentario_versao_id == self.ids[5])
                ),
                0,
            )

    def test_cascata_exclusao_conta_e_versao(self):
        self.simultaneos(["UTIL", "UTIL"])
        with Session(self.engine) as db:
            db.execute(delete(Usuario).where(Usuario.id == self.ids[1]))
            db.commit()
            self.assertEqual(servico.consultar(db, self.ids[5], None)["uteis"], 0)
            # Novo voto do autor apenas na camada repository para verificar a FK da versão.
            db.add(
                VotoComentario(
                    comentario_versao_id=self.ids[5], usuario_id=self.ids[0], voto="UTIL"
                )
            )
            db.commit()
            db.execute(delete(ComentarioVersao).where(ComentarioVersao.id == self.ids[5]))
            db.commit()
            self.assertEqual(
                db.scalar(
                    select(func.count())
                    .select_from(VotoComentario)
                    .where(VotoComentario.comentario_versao_id == self.ids[5])
                ),
                0,
            )

    def test_retirada_concorrente_nao_ressuscita_voto(self):
        barreira = Barrier(2)

        def retirar():
            with Session(self.engine) as db:
                barreira.wait(timeout=10)
                versao = comentario_repository.obter_bloqueado(db, self.ids[5])
                versao.estado = EstadoComentario.RETIRADO
                db.commit()

        def votar():
            with Session(self.engine) as db:
                usuario = db.get(Usuario, self.ids[1])
                barreira.wait(timeout=10)
                try:
                    servico.definir(db, self.ids[5], usuario, "UTIL")
                except servico.VotoComentarioError as erro:
                    self.assertEqual(erro.status_code, 404)

        with ThreadPoolExecutor(max_workers=2) as pool:
            futuros = [pool.submit(retirar), pool.submit(votar)]
            for futuro in futuros:
                futuro.result(timeout=15)
        with Session(self.engine) as db:
            with self.assertRaises(servico.VotoComentarioError):
                servico.consultar(db, self.ids[5], None)
            self.assertEqual(
                db.get(ComentarioVersao, self.ids[5]).estado, EstadoComentario.RETIRADO
            )
