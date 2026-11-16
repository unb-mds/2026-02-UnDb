"""Ampliação numérica offline; nenhum dado é publicado ou enviado à API."""

import hashlib
import json
import math
import platform
import subprocess
from collections import Counter
from datetime import datetime, timezone
from time import perf_counter_ns

import avaliar as bancada
from app.domain import filtro_moderacao as filtro


def medir_limites():
    resultados = {}
    entradas = {"numeros": "0" * 500, "quase_termo": "p0rr" * 125, "expansao_nfkd": "\ufdfa" * 500}
    for nome, texto in entradas.items():
        resultados[nome] = {}
        for variante, ativa in (("etapa1", False), ("leet", True)):
            for _ in range(3):
                filtro.categorias_para_triagem(
                    texto, disfarces_ativos=True, substituicoes_ativas=ativa
                )
            tempos = []
            for _ in range(31):
                inicio = perf_counter_ns()
                filtro.categorias_para_triagem(
                    texto, disfarces_ativos=True, substituicoes_ativas=ativa
                )
                tempos.append((perf_counter_ns() - inicio) / 1_000_000)
            resultados[nome][variante] = {
                "tempos_ms": tempos,
                "p95_ms": sorted(tempos)[math.ceil(0.95 * len(tempos)) - 1],
            }
    return {
        "caracteres": 500,
        "aquecimento": 3,
        "amostras": 31,
        "ordem": "sequencial por entrada, etapa1 depois leet; sem HTTP/banco",
        "resultados": resultados,
    }


def main():
    casos = []
    for nome in ("casos.json", "casos-leet.json"):
        casos.extend(json.loads((bancada.PASTA / nome).read_text(encoding="utf-8"))["casos"])
    assert len({c["id"] for c in casos}) == len(casos)
    resultados = []
    for caso in casos:
        texto = caso["texto"]
        assert 1 <= len(texto) <= 500
        local = {"anterior_239": bancada.categorias_lexicais(texto)}
        fluxos = {}
        for nome, ativa in (("etapa1", False), ("leet", True)):
            local[nome] = filtro.categorias_para_triagem(
                texto, disfarces_ativos=True, substituicoes_ativas=ativa
            )
            fluxos[nome] = {
                s: bancada.simular_fluxo(
                    texto, s, disfarces_ativos=True, substituicoes_ativas=ativa
                )
                for s in ("sem_sinal", "sinal", "falha")
            }
        assert set(local["etapa1"]).issubset(local["leet"])
        esperado = caso.get(
            "decisao_esperada", "PENDENTE" if caso["grupo"] == "positivo" else "PUBLICADO"
        )
        resultados.append(
            {
                **caso,
                "texto_escapado": texto.encode("unicode_escape").decode("ascii"),
                "decisao_esperada_proposta": esperado,
                "local": {
                    k: {"categorias": v, "erro": bancada.erro_binario(caso, bool(v))}
                    for k, v in local.items()
                },
                "fluxos_controlados": fluxos,
                "decisao_obtida_real": None,
                "ia_real": {"status": "NAO_EXECUTADA", "modelo_retornado": None},
            }
        )
    resumo = {}
    for nome in ("anterior_239", "etapa1", "leet"):
        contagem = Counter(r["local"][nome]["erro"] for r in resultados)
        resumo[nome] = {k: contagem[k] for k in ("TP", "FN", "FP", "TN")}
    fontes = [
        "backend/app/domain/filtro_moderacao.py",
        "backend/app/domain/triagem_comentario.py",
        "backend/app/services/moderacao_automatica_service.py",
        "backend/app/services/triagem_service.py",
        "backend/app/core/config.py",
        "docs/estudos/evidencias/issue-252/casos.json",
        "docs/estudos/evidencias/issue-252/casos-leet.json",
        "docs/estudos/evidencias/issue-252/avaliar.py",
        "docs/estudos/evidencias/issue-252/avaliar_leet.py",
    ]
    dados = {
        "data_utc": datetime.now(timezone.utc).isoformat(),
        "codigo_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=bancada.RAIZ, text=True
        ).strip(),
        "sha256_fontes_utf8_lf": {
            p: hashlib.sha256((bancada.RAIZ / p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for p in fontes
        },
        "python": platform.python_version(),
        "versao": filtro.VERSAO_SUBSTITUICOES,
        "api_real_chamadas": 0,
        "homologacao_humana": "PENDENTE",
        "modelo_configurado": "omni-moderation-latest",
        "composicao": dict(Counter(c["grupo"] for c in casos)),
        "resumo_local": resumo,
        "casos": resultados,
        "desempenho": medir_limites(),
    }
    (bancada.PASTA / "resultados-leet.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    linhas = [
        "# Resultados da ampliação numérica — #252\n",
        "[Relatório](../../implementacao-substituicoes-issue-252.md) · [Dados completos](resultados-leet.json)\n",
        "Rótulos exploratórios; IA real não executada. Fluxos usam mocks, sem publicação.\n",
        "| Camada | TP | FN | FP | TN |",
        "|---|---:|---:|---:|---:|",
    ]
    for nome, r in resumo.items():
        linhas.append(f"| {nome} | {r['TP']} | {r['FN']} | {r['FP']} | {r['TN']} |")
    linhas += [
        "\n| ID | Texto escapado | Grupo | Antes | Depois | Erro depois | Decisão controlada antes/depois (IA sem sinal) |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in resultados:
        anterior = ", ".join(r["local"]["etapa1"]["categorias"]) or "∅"
        depois = ", ".join(r["local"]["leet"]["categorias"]) or "∅"
        estados = " / ".join(
            r["fluxos_controlados"][v]["sem_sinal"]["estado_simulado"] for v in ("etapa1", "leet")
        )
        linhas.append(
            f"| {r['id']} | `{r['texto_escapado']}` | {r['grupo']} | {anterior} | {depois} | {r['local']['leet']['erro'] or 'contextual'} | {estados} |"
        )
    (bancada.PASTA / "resultados-leet.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "composicao": dados["composicao"],
                "resumo_local": resumo,
                "fp": [r["id"] for r in resultados if r["local"]["leet"]["erro"] == "FP"],
            }
        )
    )


if __name__ == "__main__":
    main()
