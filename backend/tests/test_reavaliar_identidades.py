import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-reavaliacao")

import unittest
from unittest.mock import Mock
from sqlalchemy import func, select
from app.commands.reavaliar_identidades import aplicar, carregar
from app.models import IdentidadeDocente, Professor
from tests import test_identidade_docente as fixture


class ReavaliarTest(unittest.TestCase):
    setUp = fixture.IdentidadeTest.setUp
    tearDown = fixture.IdentidadeTest.tearDown
    salvar = fixture.IdentidadeTest.salvar
    item = fixture.IdentidadeTest.item

    def test_selecao_so_inconclusivas_sem_escrever(self):
        self.salvar(motivo="CONSULTA_INCONCLUSIVA")
        self.salvar("05", motivo="PERFIL_AUSENTE")
        self.salvar("06", motivo="COMPATIVEL")
        self.db.commit()
        antes = self.db.scalar(select(func.count()).select_from(Professor))
        itens, ignoradas = carregar(self.db)
        self.assertEqual(len(itens), 1)
        self.assertEqual(ignoradas, [])
        self.assertEqual(itens[0].oferta.componente_id, self.oferta.componente_id)
        self.assertEqual(self.item().estado, "PENDENTE")
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Professor)), antes)

    def test_reavaliacao_usa_regra_existente_sem_alterar_turma(self):
        turma, _ = self.salvar(motivo="CONSULTA_INCONCLUSIVA")
        self.db.commit()
        professor = turma.professores[0].id
        itens, _ = carregar(self.db)
        consulta = Mock(consultar=Mock(return_value=("COMPATIVEL", [fixture.CANDIDATO])))
        estado = aplicar(self.db, itens[0], consulta)
        self.db.commit()
        self.assertEqual(estado, "APLICADA")
        self.assertEqual(turma.professores[0].id, professor)
        self.assertEqual(self.db.get(IdentidadeDocente, "1234").professor_id, professor)
        self.assertEqual(self.item().versao, itens[0].versao + 1)

    def test_versao_alterada_ou_decisao_humana_nao_e_sobrescrita(self):
        self.salvar(motivo="CONSULTA_INCONCLUSIVA")
        self.db.commit()
        itens, _ = carregar(self.db)
        consulta = Mock()
        self.item().versao += 1
        self.db.commit()
        self.assertEqual(aplicar(self.db, itens[0], consulta), "ALTERADA_DESDE_PREVIA")
        consulta.consultar.assert_not_called()
        self.db.rollback()
        itens, _ = carregar(self.db)
        self.item().estado = "SEPARADA"
        self.item().humana = True
        self.db.commit()
        self.assertEqual(aplicar(self.db, itens[0], consulta), "ALTERADA_DESDE_PREVIA")
        consulta.consultar.assert_not_called()

    def test_uniao_de_registros_existentes_continua_administrativa(self):
        self.salvar(motivo="COMPATIVEL")
        turma, _ = self.salvar("05", motivo="CONSULTA_INCONCLUSIVA")
        self.db.commit()
        origem = turma.professores[0].id
        itens, _ = carregar(self.db)
        consulta = Mock(consultar=Mock(return_value=("COMPATIVEL", [fixture.CANDIDATO])))
        self.assertEqual(aplicar(self.db, itens[0], consulta), "CONFIRMADA")
        self.db.commit()
        self.assertEqual(turma.professores[0].id, origem)

    def test_componente_alterado_desde_consulta_nao_e_associado(self):
        self.salvar(motivo="CONSULTA_INCONCLUSIVA")
        self.db.commit()
        itens, _ = carregar(self.db)
        from app.models import Disciplina

        disciplina = self.db.scalar(
            select(Disciplina).where(Disciplina.codigo == itens[0].oferta.componente_codigo)
        )
        disciplina.identificador_externo = "outro-id"
        self.db.commit()
        consulta = Mock()
        self.assertEqual(aplicar(self.db, itens[0], consulta), "ALTERADA_DESDE_PREVIA")
        consulta.consultar.assert_not_called()
