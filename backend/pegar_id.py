"""Lista os identificadores das unidades disponíveis no formulário público do SIGAA."""

import sys
from urllib.request import Request, urlopen

from app.scrapers.sigaa_poc import TURMAS_PORTAL_URL, USER_AGENT, parse_form


def listar_unidades(html: str) -> list[tuple[str, str]]:
    formulario = parse_form(html)
    opcoes = formulario.options.get("formTurma:inputDepto")
    if not opcoes:
        raise ValueError("O formulário SIGAA não contém unidades.")
    return [
        (identificador, nome)
        for identificador, nome in opcoes
        if identificador and identificador != "0"
    ]


def main() -> None:
    try:
        request = Request(TURMAS_PORTAL_URL, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=30) as response:
            charset = response.headers.get_content_charset() or "iso-8859-1"
            html = response.read().decode(charset, errors="replace")
        for identificador, nome in listar_unidades(html):
            print(f"{identificador} -> {nome}")
    except (OSError, ValueError) as erro:
        print(f"Não foi possível listar as unidades do SIGAA: {erro}", file=sys.stderr)
        raise SystemExit(1) from erro


if __name__ == "__main__":
    main()
