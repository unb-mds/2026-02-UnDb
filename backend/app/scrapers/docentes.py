"""Busca docente pública; nenhuma conexão com o banco ou união por nome."""

import re
import time
import unicodedata
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = "https://sigaa.unb.br"
BUSCA = BASE + "/sigaa/public/docente/busca_docentes.jsf"


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = {}
        self.departamentos = []
        self.docentes = []
        self.textos = []
        self._select = None
        self._option = None
        self._option_text = []
        self._campo = None
        self._texto = []
        self._docente = {}

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "input" and attr.get("type") == "hidden":
            self.hidden[attr["name"]] = attr.get("value", "")
        if tag == "select":
            self._select = attr.get("name")
        if tag == "option" and self._select == "form:departamento":
            self._option = attr.get("value")
            self._option_text = []
        if tag == "tr":
            self._docente = {}
        if tag == "span" and attr.get("class") in ("nome", "departamento"):
            self._campo = attr["class"]
            self._texto = []
        if tag == "a":
            href = urljoin(BUSCA, attr.get("href", ""))
            url = urlparse(href)
            if url.netloc == "sigaa.unb.br" and url.path == "/sigaa/public/docente/portal.jsf":
                siape = parse_qs(url.query).get("siape", [""])[0]
                if siape.isdigit():
                    self._docente.update(identificador_url=siape, perfil_url=href)

    def handle_data(self, data):
        self.textos.append(data)
        if self._option is not None:
            self._option_text.append(data)
        if self._campo:
            self._texto.append(data)

    def handle_endtag(self, tag):
        if tag == "option" and self._option is not None:
            self.departamentos.append(
                {"id": self._option, "nome": " ".join("".join(self._option_text).split())}
            )
            self._option = None
        if tag == "select":
            self._select = None
        if tag == "span" and self._campo:
            self._docente[self._campo] = " ".join("".join(self._texto).split())
            self._campo = None
        if tag == "tr" and self._docente.get("nome") and self._docente.get("identificador_url"):
            self.docentes.append(self._docente.copy())
            self._docente = {}

    @property
    def total(self):
        texto = " ".join(self.textos)
        totais = re.findall(
            r"Docentes encontrados\s*\((\d+)\)|\b(\d+)\s+docentes encontrados", texto, re.I
        )
        numeros = {int(a or b) for a, b in totais}
        if len(numeros) > 1:
            raise ValueError("Totais divergentes na página; investigar antes de usar.")
        return next(iter(numeros), None)


def ler(opener, request, esperado):
    with opener.open(request, timeout=30) as response:
        if urlparse(response.geturl()).path != esperado:
            raise ValueError("SIGAA redirecionou a consulta; resultado não verificado.")
        html = response.read().decode(response.headers.get_content_charset() or "iso-8859-1")
    if not html:
        raise ValueError("SIGAA respondeu sem conteúdo.")
    return html


def buscar(nome, departamento):
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    opener.addheaders = [("User-Agent", "G7-SIGAA-POC/1.0 (academic viability check)")]
    # A consulta JSF exige sessão iniciada no portal e ViewState da mesma sessão.
    ler(opener, BASE + "/sigaa/public/home.jsf", "/sigaa/public/home.jsf")
    form = Pagina()
    form.feed(ler(opener, BUSCA + "?aba=p-ensino", urlparse(BUSCA).path))
    if "javax.faces.ViewState" not in form.hidden:
        raise ValueError("ViewState não encontrado.")
    if departamento not in {d["id"] for d in form.departamentos}:
        raise ValueError("Departamento não existe no formulário atual.")
    payload = {
        **form.hidden,
        "form:nome": nome,
        "form:departamento": departamento,
        "form:buscar": "Buscar",
    }
    request = Request(
        BUSCA,
        data=urlencode(payload).encode(),
        headers={"Origin": BASE, "Referer": BUSCA + "?aba=p-ensino"},
    )
    pagina = Pagina()
    pagina.feed(ler(opener, request, urlparse(BUSCA).path))
    if pagina.total is None or pagina.total != len(pagina.docentes):
        raise ValueError("Total ausente ou diferente do extraído; possível paginação/formato novo.")
    ids = [d["identificador_url"] for d in pagina.docentes]
    return form.departamentos, {
        "nome": nome,
        "departamento_id": departamento,
        "total_reportado": pagina.total,
        "total_extraido": len(ids),
        "identificadores_repetidos": len(ids) - len(set(ids)),
        "docentes": pagina.docentes,
    }


class Disciplinas(HTMLParser):
    """Extrai somente linhas da aba graduação, preservando semestre e repetições."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.found = False
        self.periodo = None
        self.cell = None
        self.text = []
        self.row = {}
        self.rows = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div":
            if a.get("id") == "turmas-graduacao":
                self.depth = 1
                self.found = True
                self.periodo = None
            elif self.depth:
                self.depth += 1
        if not self.depth:
            return
        if tag == "tr":
            self.row = {}
        if tag == "td":
            self.cell = a.get("class", "nome")
            self.text = []
        if tag == "a" and self.cell == "nome":
            match = re.search(r"/visualizarComponente/(\d+)(?:$|[?;])", a.get("href", ""))
            if match:
                self.row["componente_id"] = match.group(1)

    def handle_data(self, text):
        if self.depth and self.cell is not None:
            self.text.append(text)

    def handle_endtag(self, tag):
        if tag == "div" and self.depth:
            self.depth -= 1
        if not self.depth:
            return
        if tag == "td" and self.cell is not None:
            value = " ".join("".join(self.text).split())
            if self.cell == "anoPeriodo":
                # A fonte também possui blocos históricos só com o ano.
                # Preservar literalmente: 2019 não comprova 2019.1 ou 2019.2.
                if not re.fullmatch(r"\d{4}(?:\.[12])?", value):
                    raise ValueError("Formato de período desconhecido no perfil.")
                self.periodo = value
            elif self.cell in ("codigo", "nome"):
                self.row[self.cell] = value
            self.cell = None
        if tag == "tr" and self.row.get("codigo"):
            if not self.periodo or not self.row.get("componente_id"):
                raise ValueError("Disciplina sem semestre ou identificador de componente.")
            self.rows.append({"periodo": self.periodo, **self.row})


def normalizar(nome):
    texto = unicodedata.normalize("NFKD", nome)
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).casefold().split())


class NomePerfil(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.capturar = False
        self.nome = []

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            if dict(attrs).get("id") == "id-docente":
                self.depth = 1
            elif self.depth:
                self.depth += 1
        if tag == "h3" and self.depth:
            self.capturar = True

    def handle_data(self, data):
        if self.capturar:
            self.nome.append(data)

    def handle_endtag(self, tag):
        if tag == "h3":
            self.capturar = False
        if tag == "div" and self.depth:
            self.depth -= 1


def coletar_perfil(docente):
    url = (
        BASE
        + "/sigaa/public/docente/disciplinas.jsf?"
        + urlencode({"siape": docente["identificador_url"]})
    )
    op = build_opener()
    op.addheaders = [("User-Agent", "G7-SIGAA-POC/1.0 (academic viability check)")]
    html = ler(op, url, "/sigaa/public/docente/disciplinas.jsf")
    p = NomePerfil()
    p.feed(html)
    if normalizar(docente["nome"]) != normalizar("".join(p.nome)):
        raise ValueError("Nome do perfil não corresponde ao resultado da busca.")
    parser = Disciplinas()
    parser.feed(html)
    if not parser.found or not parser.rows:
        raise ValueError("Aba graduação sem linhas verificáveis; não presumir histórico vazio.")
    return {
        **docente,
        "url_disciplinas": url,
        "disciplinas": parser.rows,
        "periodos_sem_semestre": sorted(
            {r["periodo"] for r in parser.rows if len(r["periodo"]) == 4}
        ),
    }


class ConsultaDocentes:
    """Cache por execução; resposta incompleta nunca confirma unicidade."""

    def __init__(self):
        self.cache = {}

    def consultar(self, nome, oferta):
        chave = normalizar(nome)
        if chave not in self.cache:
            try:
                _, busca = buscar(nome, "0")
                candidatos = {
                    d["identificador_url"]: d
                    for d in busca["docentes"]
                    if normalizar(d["nome"]) == chave
                }
                if len(candidatos) > 10:
                    raise ValueError("Consulta ambígua extensa.")
                perfis = [coletar_perfil(d) for d in candidatos.values()]
                self.cache[chave] = perfis
            except Exception:
                # Não armazenar HTML/cookies/traceback na fila. Próxima execução reavalia.
                self.cache[chave] = None
            time.sleep(1)
        perfis = self.cache[chave]
        if perfis is None:
            return "CONSULTA_INCONCLUSIVA", []
        candidatos = []
        for perfil in perfis:
            compativel = bool(oferta.componente_id) and any(
                d["periodo"] == oferta.periodo
                and d["codigo"] == oferta.componente_codigo
                and d["componente_id"] == oferta.componente_id
                for d in perfil["disciplinas"]
            )
            candidatos.append(
                {
                    "identificador": perfil["identificador_url"],
                    "nome": perfil["nome"],
                    "perfil_url": perfil["perfil_url"],
                    "compativel": compativel,
                }
            )
        motivo = (
            "PERFIL_AUSENTE"
            if not candidatos
            else "HOMONIMOS"
            if len(candidatos) > 1
            else "COMPATIVEL"
            if candidatos[0]["compativel"]
            else "DISCIPLINA_NAO_CONFIRMADA"
        )
        return motivo, candidatos
