import unittest

from app.scrapers.sigaa_poc import parse_form, parse_ofertas


class SigaaPocParserTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
