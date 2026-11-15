"""Medição local da etapa #252 no limite de entrada; sem rede/banco."""

import hashlib
import json
import math
import platform
import statistics
from datetime import datetime, timezone
from time import perf_counter_ns

import avaliar


def main():
    entradas = {
        "letra_repetida": "r" * 500,
        "quase_termo": "m..." * 125,
        "frase_repetida": "vai " * 125,
        "expansao_nfkd": "\ufdfa" * 500,
        "critica": ("A didática foi ruim; tirei 4 na P1. " * 20)[:500],
        "positivo_no_limite": "ｍｅｒｄａ" + "!" * 495,
    }
    resultados = []
    for nome, texto in entradas.items():
        assert len(texto) == 500
        linha = {"id": nome, "caracteres": len(texto), "amostras": {}}
        for ativo in (False, True):
            for _ in range(3):
                avaliar.categorias_para_triagem(texto, disfarces_ativos=ativo)
            tempos = []
            for _ in range(61):
                inicio = perf_counter_ns()
                categorias = avaliar.categorias_para_triagem(texto, disfarces_ativos=ativo)
                tempos.append((perf_counter_ns() - inicio) / 1_000_000)
            linha["amostras"]["ligado" if ativo else "desligado"] = {
                "categorias": categorias,
                "tempos_ms": tempos,
                "p50_ms": statistics.median(tempos),
                "p95_ms": sorted(tempos)[math.ceil(0.95 * len(tempos)) - 1],
                "max_ms": max(tempos),
            }
        resultados.append(linha)
    fonte = avaliar.RAIZ / "backend/app/domain/filtro_moderacao.py"
    dados = {
        "data_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "filtro_sha256_utf8_lf": hashlib.sha256(
            fonte.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest(),
        "repeticoes": 61,
        "aquecimento": 3,
        "ordem": "por entrada, desligado depois ligado; sequencial sem carga HTTP",
        "resultados": resultados,
    }
    (avaliar.PASTA / "desempenho-etapa1.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                r["id"]: {k: round(v["p95_ms"], 3) for k, v in r["amostras"].items()}
                for r in resultados
            }
        )
    )


if __name__ == "__main__":
    main()
