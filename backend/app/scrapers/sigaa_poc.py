"""POC HTTP para a consulta pública de turmas do SIGAA/UnB.

Este módulo não persiste dados, não é acionado pela API e não constitui o scraper
de produção. Ele existe para reproduzir e verificar o fluxo investigado na Issue
#23: obter uma oferta pública e extrair disciplina, turma, docente e período.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
from dataclasses import asdict, dataclass, replace
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.request import (
    HTTPSHandler,
    HTTPCookieProcessor,
    Request,
    build_opener,
)

import certifi

BASE_URL = "https://sigaa.unb.br"
HOME_URL = f"{BASE_URL}/sigaa/public/home.jsf"
TURMAS_URL = f"{BASE_URL}/sigaa/public/turmas/listar.jsf"
TURMAS_PORTAL_URL = f"{TURMAS_URL}?aba=p-ensino"
USER_AGENT = "G7-SIGAA-POC/1.0 (academic viability check)"


@dataclass(frozen=True)
class Oferta:
    """Campos observados na tabela pública de turmas."""

    componente_codigo: str
    componente_nome: str
    turma_codigo: str
    periodo: str
    docentes: tuple[str, ...]
    componente_id: str | None
    unidade_id: str | None = None


class _FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.action = ""
        self.hidden: dict[str, str] = {}
        self.options: dict[str, list[tuple[str, str]]] = {}
        self.submits: list[tuple[str, str]] = []
        self._select_name: str | None = None
        self._option_value: str | None = None
        self._option_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "form" and values.get("id") == "formTurma":
            self.action = values.get("action", "")
        elif tag == "input":
            name, value = values.get("name"), values.get("value", "")
            if values.get("type") == "hidden" and name:
                self.hidden[name] = value
            elif values.get("type") == "submit" and name:
                self.submits.append((name, value))
        elif tag == "select":
            self._select_name = values.get("name")
            if self._select_name:
                self.options.setdefault(self._select_name, [])
        elif tag == "option" and self._select_name:
            self._option_value = values.get("value", "")
            self._option_text = []

    def handle_data(self, data: str) -> None:
        if self._option_value is not None:
            self._option_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "option" and self._select_name and self._option_value is not None:
            text = " ".join("".join(self._option_text).split())
            self.options[self._select_name].append((self._option_value, text))
            self._option_value = None
        elif tag == "select":
            self._select_name = None


class _TurmasParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ofertas: list[Oferta] = []
        self.total_reportado: int | None = None
        self._component_code = ""
        self._component_name = ""
        self._component_id: str | None = None
        self._in_group = False
        self._capture_component = False
        self._cell_class: str | None = None
        self._cell_data: list[str] = []
        self._row: dict[str, str] = {}
        self._in_total = False
        self._total_data: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set(values.get("class", "").split())
        if tag == "tr":
            self._in_group = "agrupador" in classes
            if not self._in_group:
                self._row = {}
        elif tag == "a" and self._in_group:
            match = re.search(r"'id':'(\d+)'", values.get("onclick", ""))
            if match:
                self._component_id = match.group(1)
        elif tag == "span" and "tituloDisciplina" in classes:
            self._capture_component = True
            self._cell_data = []
        elif tag == "td":
            self._cell_class = values.get("class")
            self._cell_data = []
            self._in_total = False
        elif tag == "br" and self._cell_class:
            self._cell_data.append(" ")
        elif tag == "b":
            self._in_total = True
            self._total_data = []

    def handle_data(self, data: str) -> None:
        if self._capture_component or self._cell_class:
            self._cell_data.append(data)
        if self._in_total:
            self._total_data.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self._capture_component:
            title = " ".join("".join(self._cell_data).split())
            code, _, name = title.partition(" - ")
            self._component_code, self._component_name = code, name
            self._capture_component = False
        elif tag == "td" and self._cell_class:
            self._row[self._cell_class] = " ".join("".join(self._cell_data).split())
            self._cell_class = None
        elif tag == "b" and self._in_total:
            match = re.search(r"(\d+)\s+turmas encontrada", " ".join(self._total_data))
            if match:
                self.total_reportado = int(match.group(1))
            self._in_total = False
        elif tag == "tr" and not self._in_group:
            if {"turma", "anoPeriodo", "nome"} <= self._row.keys() and self._component_code:
                self.ofertas.append(
                    Oferta(
                        componente_codigo=self._component_code,
                        componente_nome=self._component_name,
                        turma_codigo=self._row["turma"],
                        periodo=self._row["anoPeriodo"],
                        docentes=_docentes(self._row["nome"]),
                        componente_id=self._component_id,
                    )
                )


def _docentes(text: str) -> tuple[str, ...]:
    names = re.findall(r"(.*?)(?:\s*\(\d+h\))(?=\s|$)", text)
    docentes = tuple(" ".join(name.split()) for name in names if name.strip())
    if docentes:
        return docentes

    docente = text.strip()
    return (docente,) if docente else ()


def parse_form(html: str) -> _FormParser:
    parser = _FormParser()
    parser.feed(html)
    if "javax.faces.ViewState" not in parser.hidden:
        raise ValueError("O formulário SIGAA não contém javax.faces.ViewState.")
    return parser


def parse_ofertas(html: str) -> tuple[list[Oferta], int | None]:
    parser = _TurmasParser()
    parser.feed(html)
    return parser.ofertas, parser.total_reportado


def _option_value(options: list[tuple[str, str]], label: str) -> str:
    normalized = label.casefold()
    for value, text in options:
        if normalized in text.casefold():
            return value
    raise ValueError(f"Opção não encontrada no formulário SIGAA: {label!r}")


def _buscar_submit(submits: list[tuple[str, str]]) -> tuple[str, str]:
    for name, value in submits:
        if value.casefold() == "buscar":
            return name, value
    raise ValueError("Botão 'Buscar' não encontrado no formulário SIGAA.")


def _decode(response) -> str:  # type: ignore[no-untyped-def]
    charset = response.headers.get_content_charset() or "iso-8859-1"
    return response.read().decode(charset, errors="replace")


def coletar_ofertas_reais(
    unidade_label: str = "DEPTO CIÊNCIAS DA COMPUTAÇÃO",
    ano: str = "2026",
    periodo: str = "2",
) -> tuple[list[Oferta], int | None]:
    """Executa o fluxo HTTP público, preservando a sessão JSF em memória."""
    cookie_jar = CookieJar()
    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
)
    opener = build_opener(
        HTTPCookieProcessor(cookie_jar),
        HTTPSHandler(context=ssl_context),
)
    headers = {"User-Agent": USER_AGENT}
    _decode(opener.open(Request(HOME_URL, headers=headers), timeout=30))
    form_html = _decode(opener.open(Request(TURMAS_PORTAL_URL, headers=headers), timeout=30))
    form = parse_form(form_html)

    nivel = _option_value(form.options["formTurma:inputNivel"], "GRADUAÇÃO")
    unidade = _option_value(form.options["formTurma:inputDepto"], unidade_label)
    button_name, button_value = _buscar_submit(form.submits)
    payload = {
        "formTurma": form.hidden.get("formTurma", "formTurma"),
        "formTurma:inputNivel": nivel,
        "formTurma:inputDepto": unidade,
        "formTurma:inputAno": ano,
        "formTurma:inputPeriodo": periodo,
        button_name: button_value,
        "javax.faces.ViewState": form.hidden["javax.faces.ViewState"],
    }
    request = Request(
        TURMAS_URL,
        data=urlencode(payload).encode(),
        headers={
            **headers,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": BASE_URL,
            "Referer": TURMAS_PORTAL_URL,
        },
    )
    response = opener.open(request, timeout=30)
    if response.geturl() != TURMAS_URL:
        raise RuntimeError(f"POST redirecionado para {response.geturl()}, sem resultado de turmas.")
    ofertas, total = parse_ofertas(_decode(response))
    return [replace(oferta, unidade_id=unidade) for oferta in ofertas], total


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa a POC HTTP do SIGAA/UnB.")
    parser.add_argument("--real", action="store_true", help="faz requisições públicas ao SIGAA")
    args = parser.parse_args()
    if not args.real:
        parser.error("use --real para autorizar a consulta pública ao SIGAA")
    ofertas, total = coletar_ofertas_reais()
    print(json.dumps({"total_reportado": total, "ofertas_extraidas": len(ofertas), "primeira_oferta": asdict(ofertas[0])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
