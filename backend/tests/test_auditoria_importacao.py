import copy
import json
import unittest
from datetime import UTC, datetime
from types import SimpleNamespace

from app.domain.auditoria_importacao import auditar_cobertura
from app.services.auditoria_importacao_service import auditar_registro


class AuditoriaImportacaoTest(unittest.TestCase):
    def setUp(self):
        self.esperadas = [
            {"departamento": "CIC", "unidade_sigaa": "Computacao"},
            {"departamento": "ZERO", "unidade_sigaa": "Sem ofertas"},
        ]
        self.resultado = {
            "sucesso": True,
            "ano": "2026",
            "periodo": "2",
            "departamentos": [
                {
                    **item,
                    "sucesso": True,
                    "erros": [],
                    "total_reportado": n,
                    "ofertas_extraidas": n,
                    "ofertas_processadas": n,
                }
                for item, n in zip(self.esperadas, [3, 0])
            ],
        }

    def audit(self, **overrides):
        return auditar_cobertura(
            self.esperadas,
            self.resultado,
            **{
                "status": "sucesso",
                "ano": "2026",
                "periodo": "2",
                "extraidas": 3,
                "processadas": 3,
                "erro_registrado": False,
                **overrides,
            },
        )

    def test_zero_ofertas_e_denominador_dinamico_sao_validos(self):
        relatorio = self.audit()
        self.assertTrue(relatorio["completa"])
        self.assertEqual(relatorio["quantidade_esperada"], 2)
        self.assertEqual(relatorio["sem_ofertas"], ["ZERO"])

    def test_mesma_quantidade_nao_oculta_unidade_ausente_e_inesperada(self):
        self.resultado["departamentos"][1]["departamento"] = "OUTRA"
        relatorio = self.audit()
        self.assertFalse(relatorio["completa"])
        self.assertEqual(relatorio["ausentes"], ["ZERO"])
        self.assertEqual(relatorio["inesperadas"], ["OUTRA"])

    def test_duplicatas_do_resultado_sao_inconsistencia(self):
        self.resultado["departamentos"].append(copy.deepcopy(self.resultado["departamentos"][1]))
        relatorio = self.audit()
        self.assertFalse(relatorio["completa"])
        self.assertEqual(relatorio["duplicadas_processadas"], ["ZERO"])

    def test_duplicatas_do_denominador_nao_comprovam_cobertura(self):
        self.esperadas.append(self.esperadas[1].copy())
        relatorio = self.audit()
        self.assertFalse(relatorio["completa"])
        self.assertEqual(relatorio["duplicadas_esperadas"], ["ZERO"])

    def test_unidade_falha_com_zero_ofertas_nao_e_classificada_como_vazia(self):
        self.resultado["departamentos"][1].update(sucesso=False, erros=["erro privado"])
        relatorio = self.audit()
        self.assertFalse(relatorio["completa"])
        self.assertEqual(relatorio["unidades_com_falha"], ["ZERO"])
        self.assertEqual(relatorio["sem_ofertas"], [])
        self.assertNotIn("erro privado", json.dumps(relatorio))

    def test_status_interrompido_ou_erro_registrado_impedem_sucesso(self):
        self.assertFalse(self.audit(status="em_andamento")["completa"])
        self.assertFalse(self.audit(erro_registrado=True)["completa"])

    def test_contagens_parciais_totais_e_periodo_divergentes(self):
        self.resultado["departamentos"][0]["ofertas_processadas"] = 2
        self.assertFalse(self.audit(processadas=2)["completa"])
        self.resultado["departamentos"][0]["ofertas_processadas"] = 3
        self.assertFalse(self.audit(extraidas=4)["totais_conferem"])
        self.assertFalse(self.audit(ano="2027")["periodo_confere"])

    def test_contagem_ausente_nao_vira_zero(self):
        del self.resultado["departamentos"][1]["ofertas_extraidas"]
        self.assertFalse(self.audit()["completa"])

    def test_total_reportado_ausente_ou_invalido_nao_comprova_extracao(self):
        unidade = self.resultado["departamentos"][0]
        for total in (None, "3", True, -1, 2):
            with self.subTest(total=total):
                unidade["total_reportado"] = total
                relatorio = self.audit()
                self.assertFalse(relatorio["completa"])
                self.assertEqual(relatorio["contagens_inconsistentes"], ["CIC"])
        del unidade["total_reportado"]
        self.assertFalse(self.audit()["completa"])

    def test_zero_sem_total_confirmado_nao_e_classificado_como_unidade_sem_ofertas(self):
        unidade = self.resultado["departamentos"][1]
        for total in (None, False, 1):
            with self.subTest(total=total):
                unidade["total_reportado"] = total
                relatorio = self.audit()
                self.assertFalse(relatorio["completa"])
                self.assertEqual(relatorio["contagens_inconsistentes"], ["ZERO"])
                self.assertEqual(relatorio["sem_ofertas"], [])

    def test_lista_vazia_ou_resultado_sem_detalhes_nao_comprovam_cobertura(self):
        self.esperadas = []
        self.assertFalse(self.audit()["completa"])
        self.esperadas = [{"departamento": "CIC"}]
        self.resultado = {"sucesso": False}
        self.assertEqual(self.audit()["ausentes"], ["CIC"])

    def test_resultado_malformado_falha_explicitamente(self):
        self.resultado["departamentos"] = "nao e uma lista"
        with self.assertRaises(ValueError):
            self.audit()

    def test_relatorio_preserva_escopo_historico_sem_inventar_enumeracao(self):
        registro = SimpleNamespace(
            id="execucao-teste",
            departamentos=self.esperadas,
            resultado_json=self.resultado,
            status="sucesso",
            ano="2026",
            periodo="2",
            ofertas_extraidas=3,
            ofertas_processadas=3,
            erro=None,
            iniciada_em=datetime.now(UTC),
            finalizada_em=datetime.now(UTC),
        )
        relatorio = auditar_registro(registro)
        self.assertTrue(relatorio["completa"])
        self.assertFalse(relatorio["cobertura_formulario_verificada"])
        self.assertEqual(relatorio["origem_unidades"], "nao_registrada")
        registro.resultado_json["origem_unidades"] = "formulario_sigaa"
        self.assertTrue(auditar_registro(registro)["cobertura_formulario_verificada"])
