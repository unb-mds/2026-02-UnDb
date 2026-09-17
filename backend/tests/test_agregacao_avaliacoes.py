import os
import unittest

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://teste:teste@localhost:5432/teste",
)
os.environ.setdefault("SECRET_KEY", "teste-local")

from app.domain.avaliacoes import (
    AvaliacaoParaAgregacao,
    Dificuldade,
    QualidadeMaterial,
    ResultadoFactual,
    agregar_avaliacoes,
)


def avaliacao(
    *,
    didatica: int = 4,
    dificuldade: Dificuldade = Dificuldade.MEDIO,
    chamada: bool = True,
    disponibiliza_material: bool = True,
    qualidade_material: QualidadeMaterial | None = QualidadeMaterial.MEDIO,
    recomenda: bool = True,
) -> AvaliacaoParaAgregacao:
    return AvaliacaoParaAgregacao(
        didatica=didatica,
        dificuldade=dificuldade,
        chamada=chamada,
        disponibiliza_material=disponibiliza_material,
        qualidade_material=qualidade_material,
        recomenda=recomenda,
    )


class AgregacaoAvaliacoesTest(unittest.TestCase):
    def test_agrega_cinco_criterios_com_desempates_aprovados(self) -> None:
        resultado = agregar_avaliacoes(
            [
                avaliacao(
                    dificuldade=Dificuldade.FACIL,
                    qualidade_material=QualidadeMaterial.RUIM,
                ),
                avaliacao(
                    dificuldade=Dificuldade.MEDIO,
                    chamada=False,
                    qualidade_material=QualidadeMaterial.BOM,
                    recomenda=False,
                ),
                avaliacao(
                    dificuldade=Dificuldade.DIFICIL,
                    qualidade_material=QualidadeMaterial.MEDIO,
                ),
            ]
        )

        self.assertEqual(resultado.didatica, 4.0)
        self.assertEqual(resultado.dificuldade, Dificuldade.DIFICIL)
        self.assertIs(resultado.chamada, True)
        self.assertIs(resultado.disponibiliza_material, True)
        self.assertEqual(resultado.qualidade_material, QualidadeMaterial.BOM)
        self.assertEqual(resultado.recomenda, 67)

    def test_retorna_conflitante_em_empate_factual_e_oculta_qualidade(self) -> None:
        resultado = agregar_avaliacoes(
            [
                avaliacao(),
                avaliacao(),
                avaliacao(
                    chamada=False,
                    disponibiliza_material=False,
                    qualidade_material=None,
                ),
                avaliacao(
                    chamada=False,
                    disponibiliza_material=False,
                    qualidade_material=None,
                ),
            ]
        )

        self.assertEqual(resultado.chamada, ResultadoFactual.CONFLITANTE)
        self.assertEqual(
            resultado.disponibiliza_material,
            ResultadoFactual.CONFLITANTE,
        )
        self.assertIsNone(resultado.qualidade_material)

    def test_arredonda_metades_para_cima(self) -> None:
        didaticas = [4, 4, 4, 5, 4, 4, 4, 5]
        recomendacoes = [True, False, False, False, False, False, False, False]
        resultado = agregar_avaliacoes(
            [
                avaliacao(didatica=didatica, recomenda=recomenda)
                for didatica, recomenda in zip(didaticas, recomendacoes, strict=True)
            ]
        )

        self.assertEqual(resultado.didatica, 4.3)
        self.assertEqual(resultado.recomenda, 13)

    def test_rejeita_lista_vazia(self) -> None:
        with self.assertRaisesRegex(ValueError, "ao menos uma avaliacao"):
            agregar_avaliacoes([])


if __name__ == "__main__":
    unittest.main()
