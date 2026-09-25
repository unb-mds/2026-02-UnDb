import unittest

from app.scrapers.sigaa_poc import parse_form, parse_ofertas
from pegar_id import listar_unidades


class SigaaPocParserTest(unittest.TestCase):
    def test_lista_ids_de_todas_as_unidades_do_formulario(self) -> None:
        html = """
        <form id="formTurma">
          <input type="hidden" name="javax.faces.ViewState" value="state-atual">
          <select name="formTurma:inputDepto">
            <option value="0">-- SELECIONE --</option>
            <option value="508">DEPTO CIÊNCIAS DA COMPUTAÇÃO</option>
            <option value="509">DEPARTAMENTO DE MATEMÁTICA</option>
          </select>
        </form>
        """

        self.assertEqual(listar_unidades(html), [
            ("508", "DEPTO CIÊNCIAS DA COMPUTAÇÃO"),
            ("509", "DEPARTAMENTO DE MATEMÁTICA"),
        ])

    def test_form_extracts_jsf_state_options_and_dynamic_submit(self) -> None:
        form = parse_form("""
        <form id="formTurma" action="/sigaa/public/turmas/listar.jsf">
          <input type="hidden" name="formTurma" value="formTurma">
          <input type="hidden" name="javax.faces.ViewState" value="state-atual">
          <select name="formTurma:inputNivel"><option value="G">GRADUAÇÃO</option></select>
          <select name="formTurma:inputDepto"><option value="508">DEPTO CIÊNCIAS DA COMPUTAÇÃO</option></select>
          <input type="submit" name="formTurma:j_id_11" value="Buscar">
        </form>
        """)

        self.assertEqual(form.hidden["javax.faces.ViewState"], "state-atual")
        self.assertEqual(form.options["formTurma:inputNivel"], [("G", "GRADUAÇÃO")])
        self.assertEqual(form.submits, [("formTurma:j_id_11", "Buscar")])

    def test_oferta_preserves_relationship_and_identifiers(self) -> None:
        ofertas, total = parse_ofertas("""
        <table><tbody>
          <tr class="agrupador"><td><a onclick="jsfcljs({'id':'177942'})"><span class="tituloDisciplina">CIC0002 - FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO</span></a></td></tr>
          <tr class="linhaPar"><td class="turma">01</td><td class="anoPeriodo">2026.2</td><td class="nome">MARIA EMILIA MACHADO TELLES WALTER (60h)</td></tr>
        </tbody><tfoot><tr><td><b>1 turmas encontrada(s)</b></td></tr></tfoot></table>
        """)

        self.assertEqual(total, 1)
        self.assertEqual(ofertas[0].componente_codigo, "CIC0002")
        self.assertEqual(ofertas[0].componente_nome, "FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO")
        self.assertEqual(ofertas[0].turma_codigo, "01")
        self.assertEqual(ofertas[0].periodo, "2026.2")
        self.assertEqual(ofertas[0].docentes, ("MARIA EMILIA MACHADO TELLES WALTER",))
        self.assertEqual(ofertas[0].componente_id, "177942")

    def test_oferta_sem_docente_preserva_ausencia(self) -> None:
        ofertas, total = parse_ofertas("""
        <table><tbody>
          <tr class="agrupador"><td><span class="tituloDisciplina">CIC0002 - FUNDAMENTOS TEORICOS DA COMPUTACAO</span></td></tr>
          <tr class="linhaPar"><td class="turma">01</td><td class="anoPeriodo">2026.2</td><td class="nome"></td></tr>
        </tbody><tfoot><tr><td><b>1 turmas encontrada(s)</b></td></tr></tfoot></table>
        """)

        self.assertEqual(total, 1)
        self.assertEqual(ofertas[0].docentes, ())

    def test_marcador_docente_a_definir_nao_cria_professor(self) -> None:
        ofertas, total = parse_ofertas("""
        <table><tbody>
          <tr class="agrupador"><td><span class="tituloDisciplina">FCE0794 - DISCIPLINA</span></td></tr>
          <tr class="linhaPar"><td class="turma">03</td><td class="anoPeriodo">2026.2</td><td class="nome">A DEFINIR DOCENTE (60h)</td></tr>
        </tbody><tfoot><tr><td><b>1 turmas encontrada(s)</b></td></tr></tfoot></table>
        """)

        self.assertEqual(total, 1)
        self.assertEqual(ofertas[0].docentes, ())

    def test_sem_resultados_explicitos_retorna_total_zero(self) -> None:
        ofertas, total = parse_ofertas(
            "<div class='info'>N&#227;o foram encontrados resultados para a busca "
            "com estes par&#226;metros.</div>"
        )

        self.assertEqual(ofertas, [])
        self.assertEqual(total, 0)

    def test_pagina_sem_resultado_nem_mensagem_mantem_total_desconhecido(self) -> None:
        ofertas, total = parse_ofertas("<div>Resposta inesperada do SIGAA</div>")

        self.assertEqual(ofertas, [])
        self.assertIsNone(total)


class SigaaPocMultipleDocentesParserTest(unittest.TestCase):
    def test_oferta_preserves_multiple_docentes_from_sigaa_cell(self) -> None:
        ofertas, total = parse_ofertas("""
        <table><tbody>
          <tr class="agrupador"><td><a onclick="jsfcljs({'id':'177944'})"><span class="tituloDisciplina">CIC0004 - ALGORITMOS E PROGRAMAÇÃO DE COMPUTADORES</span></a></td></tr>
          <tr class="linhaImpar">
            <td class="turma" align="center">02</td>
            <td class="anoPeriodo" align="center">2026.2</td>
            <td class="nome">YURI COSSICH LAVINAS (60h)<br />JOAO GABRIEL ROSSI DE BORBA (30h)<br /></td>
          </tr>
        </tbody><tfoot><tr><td><b>1 turmas encontrada(s)</b></td></tr></tfoot></table>
        """)

        self.assertEqual(total, 1)
        self.assertEqual(len(ofertas), 1)
        self.assertEqual(ofertas[0].componente_codigo, "CIC0004")
        self.assertEqual(ofertas[0].componente_nome, "ALGORITMOS E PROGRAMAÇÃO DE COMPUTADORES")
        self.assertEqual(ofertas[0].turma_codigo, "02")
        self.assertEqual(ofertas[0].periodo, "2026.2")
        self.assertEqual(ofertas[0].docentes, ("YURI COSSICH LAVINAS", "JOAO GABRIEL ROSSI DE BORBA"))
        self.assertEqual(ofertas[0].componente_id, "177944")


if __name__ == "__main__":
    unittest.main()
