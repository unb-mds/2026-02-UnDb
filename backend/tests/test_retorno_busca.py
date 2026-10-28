import unittest
from urllib.parse import urlencode

from pydantic import ValidationError

from app.schemas.auth import CadastroRequest


DESTINO = "/professores/11111111-1111-4111-8111-111111111111/disciplinas/22222222-2222-4222-8222-222222222222/avaliar"


class RetornoBuscaTest(unittest.TestCase):
    def cadastro(self, destino):
        return CadastroRequest(nome="Estudante", email="teste@aluno.unb.br", senha="senha-teste", return_to=destino)

    def test_preserva_rotas_antigas_e_contexto_permitido(self):
        self.assertEqual(self.cadastro(None).return_to, None)
        self.assertEqual(self.cadastro(DESTINO).return_to, DESTINO)
        for tipo in ("professores", "disciplinas"):
            for termo in ("", "Cálculo & Álgebra + CIC", "?next=externo/#fragmento"):
                with self.subTest(tipo=tipo, termo=termo):
                    retorno = DESTINO + "?" + urlencode(dict(busca=tipo, q=termo, ordem="unidade"))
                    self.assertEqual(self.cadastro(retorno).return_to, retorno)

    def test_rejeita_destinos_externos_e_parametros_nao_permitidos(self):
        for valor in (
            "https://externo.test" + DESTINO, "//externo.test" + DESTINO,
            DESTINO + "/", DESTINO + "\n", DESTINO + "#fim", DESTINO + "?",
            DESTINO + "?busca=professores&q=x&ordem=nome&token=segredo",
            DESTINO + "?busca=professores&q=x&ordem=nome&q=y",
            DESTINO + "?busca=professores&q=x&ordem=recomendacao",
            DESTINO + "?busca=outro&q=x&ordem=nome",
            DESTINO + "?busca=professores&q=%00&ordem=nome",
            DESTINO + "?busca=professores&q=%GG&ordem=nome",
            DESTINO + "?busca=professores&q=x",
        ):
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                self.cadastro(valor)

    def test_limite_total_e_2048(self):
        prefixo = DESTINO + "?busca=professores&ordem=nome&q="
        self.assertEqual(len(self.cadastro(prefixo + "a" * (2048 - len(prefixo))).return_to), 2048)
        with self.assertRaises(ValidationError):
            self.cadastro(prefixo + "a" * (2049 - len(prefixo)))
        unicode = prefixo + "😀" * (2048 - len(prefixo))
        self.assertEqual(self.cadastro(unicode).return_to, unicode)
        with self.assertRaises(ValidationError):
            self.cadastro(unicode + "😀")
