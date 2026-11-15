"""Ensaio offline da #252: nunca consulta API nem publica avaliações.

Executar na raiz: python docs/estudos/evidencias/issue-252/avaliar.py
Variantes são hipóteses isoladas; nenhuma é importada pelo backend.
"""

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[3]
# Não herdar banco, chave ou flags privadas. Não há opção de rede neste script.
os.environ.update(
    DATABASE_URL="sqlite+pysqlite:///:memory:",
    MIGRATION_DATABASE_URL="sqlite+pysqlite:///:memory:",
    SECRET_KEY="ensaio-offline-252",
    OPENAI_API_KEY="",
    MODERACAO_AUTOMATICA_ATIVA="False",
    MODERACAO_FILTRO_ATIVO="False",
    MODERACAO_DISFARCES_ATIVO="False",
    MODERACAO_IA_ATIVA="False",
    MODERACAO_IA_DADOS_APROVADOS="False",
)
sys.path.insert(0, str(RAIZ / "backend"))

from app.domain.texto import normalizar_busca  # noqa: E402
from app.domain.filtro_moderacao import categorias_para_triagem, VERSAO_DISFARCES  # noqa: E402
from app.domain.triagem_comentario import (  # noqa: E402
    LISTA,
    VERSAO_LISTA,
    categorias_lexicais,
    contem_dados_sensiveis,
)
from app.models.enums import EstadoComentario as Estado  # noqa: E402
from app.schemas.triagem import ClassificacaoIA  # noqa: E402
from app.services import moderacao_automatica_service as auto  # noqa: E402
from app.services import openai_triagem  # noqa: E402

# Mapa pequeno e deliberadamente incompleto, NÃO implementação de UTS #39.
HOMOGLIFOS = str.maketrans({"а": "a", "е": "e", "о": "o", "і": "i", "с": "c"})
INVISIVEIS = str.maketrans("", "", "\u200b\u200c\u200d\ufeff\u2060")
LEET = {"a": "a4", "e": "e3", "i": "i1", "o": "o0", "s": "s5", "t": "t7"}
VARIANTES = (
    "busca_nfkd",
    "invisiveis",
    "unicode",
    "separadores_repeticoes",
    "leet_contextual",
    "leet_4_como_e",
)


def unicode_experimental(texto):
    # Reuso demonstrado da função da busca, apenas nesta bancada.
    return normalizar_busca(texto).translate(INVISIVEIS).translate(HOMOGLIFOS)


def categorias_experimentais(texto, variante):
    if variante == "busca_nfkd":
        texto = normalizar_busca(texto)
    elif variante == "invisiveis":
        texto = normalizar_busca(texto).translate(INVISIVEIS)
    else:
        texto = unicode_experimental(texto)
    categorias = set()
    for item in LISTA["termos"]:
        termo = normalizar_busca(item["termo"])
        if variante in ("busca_nfkd", "invisiveis", "unicode"):
            corpo = r"\s+".join(re.escape(p) for p in termo.split())
        else:
            partes = []
            for c in termo:
                if c.isspace():
                    partes.append(r"[\s.\-_*]{1,3}")
                    continue
                opcoes = c
                if variante in ("leet_contextual", "leet_4_como_e"):
                    opcoes = LEET.get(c, c)
                if variante == "leet_4_como_e" and termo == "merda" and c == "e":
                    opcoes = "e34"  # hipótese específica, não regra universal 4→e
                partes.append("[" + re.escape(opcoes) + "]{1,4}")
                partes.append(r"[\s.\-_*]{0,3}")
            # O último separador não faz parte da palavra.
            if not termo[-1].isspace():
                partes.pop()
            corpo = "".join(partes)
        if re.search(r"(?<!\w)" + corpo + r"(?!\w)", texto):
            categorias.add(item["categoria"])
    return sorted(categorias)


def erro_binario(caso, sinal):
    if caso["grupo"] == "contextual":
        return None
    if caso["grupo"] == "positivo" and not sinal:
        return "FN"
    if caso["grupo"] == "negativo" and sinal:
        return "FP"
    return "TP" if sinal else "TN"


def simular_fluxo(texto, cenario, *, disfarces_ativos=False):
    """Executa processar real com repositórios/IA substituídos, sem banco/HTTP.

    PUBLICADO significa somente estado de um objeto em memória, não publicação.
    A flag seleciona o filtro real anterior ou o complemento implementado.
    """
    versao = SimpleNamespace(
        id=uuid4(),
        avaliacao_id=uuid4(),
        estado=Estado.PENDENTE,
        texto=texto,
        avaliacao=SimpleNamespace(usuario=SimpleNamespace(nome="", email="")),
    )
    db = MagicMock()
    resultado = ClassificacaoIA(
        categorias=["harassment"] if cenario == "sinal" else [],
        sinalizado=cenario == "sinal",
        modelo="omni-moderation-latest",
    )
    with ExitStack() as stack:
        for flag in (
            "MODERACAO_AUTOMATICA_ATIVA",
            "MODERACAO_FILTRO_ATIVO",
            "MODERACAO_IA_ATIVA",
            "MODERACAO_IA_DADOS_APROVADOS",
        ):
            stack.enter_context(patch.object(auto.config, flag, True))
        stack.enter_context(patch.object(auto.config, "OPENAI_API_KEY", "fixture-offline"))
        stack.enter_context(
            patch.object(auto.config, "MODERACAO_DISFARCES_ATIVO", disfarces_ativos)
        )
        stack.enter_context(patch.object(auto.limite, "reservar", return_value=True))
        for nome, retorno in (
            ("obter_por_id", versao),
            ("obter_bloqueado", versao),
            ("obter_atual_por_avaliacao", None),
        ):
            stack.enter_context(
                patch.object(auto.comentario_repository, nome, return_value=retorno)
            )
        auditoria = stack.enter_context(
            patch.object(auto.moderacao_repository, "registrar_decisao")
        )
        opcoes = (
            {"side_effect": openai_triagem.TriagemIndisponivel()}
            if cenario == "falha"
            else {"return_value": resultado}
        )
        chamada = stack.enter_context(patch.object(openai_triagem, "classificar", **opcoes))
        # Defesa adicional contra acesso de rede acidental no ensaio.
        stack.enter_context(
            patch("socket.create_connection", side_effect=AssertionError("sem rede"))
        )
        estado = auto.processar(db, versao.id)
        assert estado in (Estado.PENDENTE, Estado.PUBLICADO)
        assert versao.texto == texto, "texto original deve ser preservado"
        assert auditoria.call_count == int(estado == Estado.PUBLICADO)
        if cenario != "sem_sinal":
            assert estado == Estado.PENDENTE
        return {"estado_simulado": estado.value, "ia_mock_chamada": chamada.called}


def resumo(casos, chave):
    contagem = Counter(c["local"][chave]["erro"] for c in casos)
    return {k: contagem[k] for k in ("TP", "FN", "FP", "TN")}


def main():
    corpus = json.loads((PASTA / "casos.json").read_text(encoding="utf-8"))
    assert corpus["revisores_humanos"] == [], "rever metadados após homologação"
    assert len({c["id"] for c in corpus["casos"]}) == len(corpus["casos"])
    casos = []
    for caso in corpus["casos"]:
        assert 1 <= len(caso["texto"]) <= 500
        local = {"atual": categorias_lexicais(caso["texto"])}
        local.update({v: categorias_experimentais(caso["texto"], v) for v in VARIANTES})
        local["complementar_implementado"] = categorias_para_triagem(
            caso["texto"], disfarces_ativos=True
        )
        esperado = caso.get(
            "decisao_esperada", "PENDENTE" if caso["grupo"] == "positivo" else "PUBLICADO"
        )
        linha = {
            **caso,
            "texto_escapado": caso["texto"].encode("unicode_escape").decode("ascii"),
            "decisao_esperada_proposta": esperado,
            "local": {
                v: {"categorias": cats, "erro": erro_binario(caso, bool(cats))}
                for v, cats in local.items()
            },
            "barreira_privacidade": contem_dados_sensiveis(caso["texto"]),
            "ia_real": {"status": "NAO_EXECUTADA", "sinalizado": None, "modelo_retornado": None},
            "triagem_combinada_real": {"decisao_obtida": None, "erro": None},
            "controle_fluxo_atual": {
                s: simular_fluxo(caso["texto"], s) for s in ("sem_sinal", "sinal", "falha")
            },
            "controle_fluxo_complementar": {
                s: simular_fluxo(caso["texto"], s, disfarces_ativos=True)
                for s in ("sem_sinal", "sinal", "falha")
            },
        }
        # Apenas resultado condicional; não mede eficácia da API.
        estado = linha["controle_fluxo_atual"]["sem_sinal"]["estado_simulado"]
        linha["controle_fluxo_atual"]["sem_sinal"].update(
            decisao_esperada_proposta=esperado,
            divergencia=None if esperado is None else estado != esperado,
            erro=erro_binario(caso, estado == "PENDENTE"),
        )
        estado_novo = linha["controle_fluxo_complementar"]["sem_sinal"]["estado_simulado"]
        linha["controle_fluxo_complementar"]["sem_sinal"].update(
            decisao_esperada_proposta=esperado,
            divergencia=None if esperado is None else estado_novo != esperado,
            erro=erro_binario(caso, estado_novo == "PENDENTE"),
        )
        casos.append(linha)
    fontes = [
        "backend/app/domain/triagem_comentario.py",
        "backend/app/domain/texto.py",
        "backend/app/domain/filtro_moderacao.py",
        "backend/app/core/config.py",
        "backend/app/data/termos_moderacao.json",
        "backend/app/services/moderacao_automatica_service.py",
        "backend/app/services/triagem_service.py",
        "backend/app/services/openai_triagem.py",
        "docs/estudos/evidencias/issue-252/casos.json",
        "docs/estudos/evidencias/issue-252/avaliar.py",
    ]
    dados = {
        "data_utc": datetime.now(timezone.utc).isoformat(),
        "codigo_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True
        ).strip(),
        "python": platform.python_version(),
        "unicode_db": unicodedata.unidata_version,
        "sha256_normalizacao": "UTF-8 com finais de linha LF",
        "sha256_fontes": {
            p: hashlib.sha256((RAIZ / p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for p in fontes
        },
        "lista": VERSAO_LISTA,
        "integracao": openai_triagem.VERSAO_INTEGRACAO,
        "versao_complemento": VERSAO_DISFARCES,
        "modelo_configurado_na_base": "omni-moderation-latest",
        "api_real_chamadas": 0,
        "homologacao_humana": "PENDENTE",
        "composicao": dict(Counter(c["grupo"] for c in casos)),
        "resumo_local": {
            v: resumo(casos, v) for v in ("atual", *VARIANTES, "complementar_implementado")
        },
        "casos": casos,
    }
    (PASTA / "resultados-etapa1.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    linhas = [
        "# Resultados da etapa inicial — Issue #252\n",
        "[Relatório da implementação](../../implementacao-ofensas-disfarcadas-issue-252.md) · "
        "[Dados completos](resultados-etapa1.json) · [Corpus](casos.json)\n",
        "Rótulos propostos; revisão humana pendente. API real e triagem real não executadas. "
        "Os controles usam mocks e o serviço real com o complemento ligado/desligado; "
        "não medem qualidade da IA. Os candidatos experimentais permanecem para comparação.\n",
        "| Variante local | TP | FN | FP | TN |",
        "|---|---:|---:|---:|---:|",
    ]
    for v, r in dados["resumo_local"].items():
        linhas.append(f"| {v} | {r['TP']} | {r['FN']} | {r['FP']} | {r['TN']} |")
    linhas += [
        "\nContextuais excluídos de TP/FN/FP/TN; sinal lexical não prova ofensa.\n",
        "Códigos dos controles: P = PENDENTE, U = PUBLICADO apenas no objeto em memória. "
        "Sempre sem avaliação persistida ou publicada.\n",
        "| ID | Entrada escapada | Grupo | Local atual | Erro local | Esperada proposta | "
        "IA real / combinada real | Mock anterior sem sinal / sinal / falha | "
        "Complemento local / erro | Mock complemento sem sinal / sinal / falha |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in casos:
        cats = ", ".join(c["local"]["atual"]["categorias"]) or "∅"
        estados = " / ".join(
            "P" if r["estado_simulado"] == "PENDENTE" else "U"
            for r in c["controle_fluxo_atual"].values()
        )
        estados_novos = " / ".join(
            "P" if r["estado_simulado"] == "PENDENTE" else "U"
            for r in c["controle_fluxo_complementar"].values()
        )
        novo = c["local"]["complementar_implementado"]
        cats_novas = ", ".join(novo["categorias"]) or "∅"
        linhas.append(
            f"| {c['id']} | `{c['texto_escapado']}` | {c['grupo']} | {cats} | "
            f"{c['local']['atual']['erro'] or 'contextual'} | "
            f"{c['decisao_esperada_proposta'] or 'a julgar'} | não executadas | {estados} | "
            f"{cats_novas} / {novo['erro'] or 'contextual'} | {estados_novos} |"
        )
    (PASTA / "resultados-etapa1.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(json.dumps({"composicao": dados["composicao"], "resumo_local": dados["resumo_local"]}))


if __name__ == "__main__":
    main()
