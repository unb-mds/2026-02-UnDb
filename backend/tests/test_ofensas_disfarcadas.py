"""Escopo incremental da #252 e preservação obrigatória da revisão #258."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from app.domain import filtro_moderacao as filtro
from app.domain.triagem_comentario import LISTA, categorias_lexicais


class DisfarcesTest(unittest.TestCase):
    def test_detecta_tecnicas_aprovadas(self):
        for texto, categoria in (
            ("ｍｅｒｄａ", "PALAVRAO"),
            ("𝐛𝐚𝐛𝐚𝐜𝐚", "XINGAMENTO"),
            ("mеrda", "PALAVRAO"),  # е cirílico
            ("bаbаcа", "XINGAMENTO"),  # а cirílico
            ("m.e.r.d.a", "PALAVRAO"),
            ("b-a-b-a-c-a", "XINGAMENTO"),
            ("i d i o t a", "OFENSA_PESSOAL"),
            ("m er da", "PALAVRAO"),
            ("meeeerda", "PALAVRAO"),
            ("babacaaaa", "XINGAMENTO"),
            ("ME\u200bRDA", "PALAVRAO"),
            ("idi\u200dota", "OFENSA_PESSOAL"),
            ("por\ufeffra", "PALAVRAO"),
            ("vai.se.foder", "XINGAMENTO"),
            ("M. EE. R. D. A", "PALAVRAO"),
        ):
            with self.subTest(texto=ascii(texto)):
                self.assertIn(
                    categoria, filtro.categorias_para_triagem(texto, disfarces_ativos=True)
                )

    def test_preserva_categorias_anteriores_para_toda_lista(self):
        for item in LISTA["termos"]:
            termo = item["termo"]
            for marca in ("", "\ufe0f", "\u034f"):
                texto = marca.join(termo)
                with self.subTest(termo=termo, marca=ascii(marca)):
                    original = categorias_lexicais(texto)
                    self.assertIn(item["categoria"], original)
                    self.assertTrue(
                        set(original).issubset(
                            filtro.categorias_para_triagem(texto, disfarces_ativos=True)
                        )
                    )

    def test_desligar_retorna_filtro_anterior_sem_normalizar_candidato(self):
        with patch.object(filtro, "normalizar_disfarces", side_effect=AssertionError("desligado")):
            self.assertEqual(filtro.categorias_para_triagem("m.e.r.d.a"), [])
            self.assertEqual(filtro.categorias_para_triagem("me\ufe0frda"), ["PALAVRAO"])

    def test_respeita_fronteiras_numeros_e_limites(self):
        for texto in (
            "idiotamente",
            "Otariidae",
            "prefixo_merda_sufixo",
            "prefｍｅｒｄａsuffix",
            "m3rda",
            "m4rda",
            "b4b4c4",
            "1d10ta",
            "V0u te m4t4r",
            "m....e....r....d....a",
            "m    e    r    d    a",
            "meeeeeeeerda",
            "vai....se....foder",
            "v a i    s e    f o d e r",
            "ᴍerda",
            "foda----------se",
        ):
            with self.subTest(texto=texto):
                self.assertEqual(filtro.categorias_para_triagem(texto, disfarces_ativos=True), [])
        self.assertEqual(
            filtro.categorias_para_triagem("m...e...r...d...a", disfarces_ativos=True), ["PALAVRAO"]
        )
        # O limite novo não pode retirar detecções já aceitas por espaços entre palavras.
        self.assertEqual(
            filtro.categorias_para_triagem("vai    se    foder", disfarces_ativos=True),
            ["XINGAMENTO"],
        )
        self.assertEqual(
            filtro.categorias_para_triagem("foda---se", disfarces_ativos=True), ["PALAVRAO"]
        )

    def test_falha_nao_se_transforma_em_resultado_limpo(self):
        with patch.object(filtro, "normalizar_disfarces", side_effect=ValueError("texto privado")):
            with self.assertRaises(filtro.FiltroIndisponivel) as erro:
                filtro.categorias_para_triagem("texto", disfarces_ativos=True)
        self.assertNotIn("texto privado", str(erro.exception))

    def test_entradas_no_limite_de_500_caracteres(self):
        for texto in ("m" * 500, "r" * 500, "\ufdfa" * 500, "m..." * 125):
            with self.subTest(texto=ascii(texto[:12])):
                self.assertEqual(filtro.categorias_para_triagem(texto, disfarces_ativos=True), [])
        texto = "ｍｅｒｄａ" + "!" * 495
        self.assertEqual(filtro.categorias_para_triagem(texto, disfarces_ativos=True), ["PALAVRAO"])

    def test_corpus_compara_antes_depois_sem_novos_sinais_negativos(self):
        caminho = (
            Path(__file__).resolve().parents[2] / "docs/estudos/evidencias/issue-252/casos.json"
        )
        casos = json.loads(caminho.read_text(encoding="utf-8"))["casos"]
        totais = {"atual": 0, "complementar": 0}
        for caso in casos:
            texto = caso["texto"]
            atual = categorias_lexicais(texto)
            complementar = filtro.categorias_para_triagem(texto, disfarces_ativos=True)
            with self.subTest(caso=caso["id"]):
                self.assertTrue(set(atual).issubset(complementar))
                self.assertEqual(filtro.categorias_para_triagem(texto), atual)
                if caso["grupo"] == "negativo":
                    self.assertEqual(complementar, [])
            if caso["grupo"] == "positivo":
                totais["atual"] += bool(atual)
                totais["complementar"] += bool(complementar)
        self.assertEqual(totais, {"atual": 10, "complementar": 24})


if __name__ == "__main__":
    unittest.main()
