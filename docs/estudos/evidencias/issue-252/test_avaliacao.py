"""Verificações da bancada offline; não constituem aceite das regras propostas."""

import unittest
from unittest.mock import patch

import avaliar


class BancadaTest(unittest.TestCase):
    def test_m4rda_exige_decisao_separada_de_4_para_a(self):
        self.assertEqual("m4rda".replace("4", "a"), "marda")
        self.assertEqual(avaliar.categorias_experimentais("m4rda", "leet_contextual"), [])
        self.assertEqual(avaliar.categorias_experimentais("m4rda", "leet_4_como_e"), ["PALAVRAO"])

    def test_falha_de_normalizacao_preserva_pendencia(self):
        with patch.object(
            avaliar.auto, "categorias_para_triagem", side_effect=ValueError("fixture")
        ):
            r = avaliar.simular_fluxo("Uma crítica acadêmica.", "sem_sinal")
        self.assertEqual(r, {"estado_simulado": "PENDENTE", "ia_mock_chamada": False})

    def test_numeros_nao_sao_transformados_globalmente(self):
        for texto in ("Tirei 4 e 3.", "Matriz 4 por 3.", "prefixo_m3rda_sufixo"):
            self.assertEqual(avaliar.categorias_experimentais(texto, "leet_contextual"), [])
        # O contexto lexical não resolve o contexto semântico: registrar FP, não escondê-lo.
        self.assertEqual(
            avaliar.categorias_experimentais("A variável m3rda.", "leet_contextual"), ["PALAVRAO"]
        )

    def test_preserva_original_unicode_e_limites(self):
        texto = "Que M\u200b3 R D A!"
        self.assertEqual(avaliar.categorias_lexicais(texto), [])
        self.assertEqual(avaliar.categorias_experimentais(texto, "leet_contextual"), ["PALAVRAO"])
        for texto in ("idiotamente", "Otariidae", "prefixo_merda_sufixo"):
            for v in avaliar.VARIANTES:
                self.assertEqual(avaliar.categorias_experimentais(texto, v), [])


if __name__ == "__main__":
    unittest.main()
