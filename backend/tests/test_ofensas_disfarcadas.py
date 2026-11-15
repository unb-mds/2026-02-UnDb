"""Escopo incremental da #252 e preservação obrigatória da revisão #258."""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

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


class SubstituicoesTest(unittest.TestCase):
    def analisar(self, texto):
        return filtro.categorias_para_triagem(
            texto, disfarces_ativos=True, substituicoes_ativas=True
        )

    def test_detecta_substituicoes_por_posicao_e_combinacoes(self):
        for texto, categoria in (
            ("m3rda", "PALAVRAO"),
            ("p0rra", "PALAVRAO"),
            ("P0RR4", "PALAVRAO"),
            ("b4b4c4", "XINGAMENTO"),
            ("1d10t4", "OFENSA_PESSOAL"),
            ("0t4r10", "XINGAMENTO"),
            ("v41 s3 f0d3r", "XINGAMENTO"),
            ("s3 m4t4", "AMEACA"),
            ("c4c373", "PALAVRAO"),
            ("p.0.r.r.4", "PALAVRAO"),
            ("m\u200b3 r d 4", "PALAVRAO"),
            ("p００rr4", "PALAVRAO"),
        ):
            with self.subTest(texto=texto):
                self.assertIn(categoria, self.analisar(texto))

    def test_flags_reversao_e_versao(self):
        self.assertEqual(filtro.categorias_para_triagem("m3rda", disfarces_ativos=True), [])
        self.assertEqual(filtro.categorias_para_triagem("p0rra", substituicoes_ativas=True), [])
        self.assertEqual(filtro.versao_filtro(False, True), "239-lexical-v1")
        self.assertEqual(filtro.versao_filtro(True), "252-disfarces-v1")
        self.assertEqual(filtro.versao_filtro(True, True), "252-disfarces-leet-v2")

    def test_preserva_numeros_e_fronteiras_sem_excecao_4_para_e(self):
        for texto in (
            "Tirei 3 na P1 e 4 na P2",
            "Matriz 4 por 3",
            "CIC0004 MAT0031",
            "prefixo_m3rda_sufixo",
            "p0rra_total",
            "p0rra9",
            "4m3rda",
            "m3rdas",
            "m4rda",
            "p....0....r....r....a",
            "m33333333rda",
            "007",
        ):
            with self.subTest(texto=texto):
                self.assertEqual(self.analisar(texto), [])

    def test_nao_esconde_sinais_tecnicos_ambiguos(self):
        # Não inventar exceção pela palavra "variável": sinal exige revisão humana.
        self.assertEqual(self.analisar("A variável p0rra contém a soma."), ["PALAVRAO"])
        self.assertEqual(self.analisar("A variável m3rda contém a soma."), ["PALAVRAO"])

    def test_uniao_preserva_todas_as_categorias_da_etapa_anterior(self):
        for item in LISTA["termos"]:
            for marca in ("", "\ufe0f", "\u034f"):
                texto = marca.join(item["termo"])
                with self.subTest(termo=item["termo"], marca=ascii(marca)):
                    anterior = filtro.categorias_para_triagem(texto, disfarces_ativos=True)
                    self.assertTrue(set(anterior).issubset(self.analisar(texto)))
        for texto in ("1" * 500, "0" * 500):
            self.assertEqual(self.analisar(texto), [])

    def test_falha_da_regra_numerica_nao_vira_resultado_limpo(self):
        padrao = MagicMock()
        padrao.search.side_effect = ValueError("conteúdo privado")
        with patch.object(filtro, "PADROES_LEET", ((padrao, "PALAVRAO"),)):
            with self.assertRaises(filtro.FiltroIndisponivel) as erro:
                self.analisar("m3rda")
        self.assertNotIn("privado", str(erro.exception))


if __name__ == "__main__":
    unittest.main()
