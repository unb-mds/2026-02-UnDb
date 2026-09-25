import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "teste-local")

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Avaliacao, Disciplina, Professor, Turma, Usuario  # noqa: F401
from app.routers.professores import consultar_avaliacoes_professor_disciplina
from app.scrapers.sigaa_poc import parse_ofertas
from app.services.sigaa_import_service import salvar_oferta


HTML_EXEMPLO_REAL = """
<table><tbody>
  <tr class="agrupador"><td><a onclick="jsfcljs({'id':'177942'})">
    <span class="tituloDisciplina">CIC0002 - FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO</span>
  </a></td></tr>
  <tr class="linhaPar">
    <td class="turma">01</td><td class="anoPeriodo">2026.2</td>
    <td class="nome">MARIA EMILIA MACHADO TELLES WALTER (60h)</td>
  </tr>
</tbody><tfoot><tr><td><b>1 turmas encontrada(s)</b></td></tr></tfoot></table>
"""


class FluxoSigaaIntegradoTest(unittest.TestCase):
    def test_extrai_persiste_e_disponibiliza_exemplo_real_da_poc(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)

        ofertas, total = parse_ofertas(HTML_EXEMPLO_REAL)
        self.assertEqual(total, 1)

        with Session(engine) as session:
            salvar_oferta(session, ofertas[0], "CIC")
            session.commit()

            professor = session.scalar(select(Professor))
            disciplina = session.scalar(select(Disciplina))
            self.assertIsNotNone(professor)
            self.assertIsNotNone(disciplina)

            resposta = consultar_avaliacoes_professor_disciplina(
                professor.id,
                disciplina.id,
                session,
            ).model_dump()

        engine.dispose()

        self.assertEqual(resposta["professor"]["nome"], "MARIA EMILIA MACHADO TELLES WALTER")
        self.assertEqual(resposta["disciplina"]["codigo"], "CIC0002")
        self.assertEqual(resposta["total_avaliacoes"], 0)


if __name__ == "__main__":
    unittest.main()
