"""Compara o denominador preservado de uma coleta com seu resultado integral."""

from collections import Counter


def auditar_cobertura(
    esperadas: list[dict],
    resultado: dict,
    *,
    status: str,
    ano: str,
    periodo: str,
    extraidas: int,
    processadas: int,
    erro_registrado: bool,
) -> dict:
    recebidas = resultado.get("departamentos", [])
    if not isinstance(recebidas, list):
        raise ValueError("resultado.departamentos deve ser uma lista")

    def codigos(itens):
        valores = []
        for item in itens:
            if not isinstance(item, dict) or not isinstance(item.get("departamento"), str):
                raise ValueError("cada unidade deve informar um codigo textual")
            codigo = item["departamento"].strip()
            if not codigo:
                raise ValueError("codigo de unidade vazio")
            valores.append(codigo)
        return Counter(valores)

    previstas, observadas = codigos(esperadas), codigos(recebidas)
    ausentes = sorted(previstas.keys() - observadas.keys())
    inesperadas = sorted(observadas.keys() - previstas.keys())
    repetidas_previstas = sorted(codigo for codigo, n in previstas.items() if n > 1)
    repetidas_observadas = sorted(codigo for codigo, n in observadas.items() if n > 1)
    falhas, inconsistentes, sem_ofertas = [], [], []
    soma_extraidas = soma_processadas = 0
    for item in recebidas:
        codigo = item["departamento"].strip()
        if item.get("sucesso") is not True or item.get("erros") != []:
            falhas.append(codigo)
        contagens = [item.get("ofertas_extraidas"), item.get("ofertas_processadas")]
        if any(type(n) is not int or n < 0 for n in contagens):
            inconsistentes.append(codigo)
            continue
        coletadas, persistidas = contagens
        soma_extraidas += coletadas
        soma_processadas += persistidas
        if coletadas != persistidas or (
            item.get("total_reportado") is not None
            and (type(item["total_reportado"]) is not int or item["total_reportado"] != coletadas)
        ):
            inconsistentes.append(codigo)
        if coletadas == 0 and item.get("sucesso") is True and item.get("erros") == []:
            sem_ofertas.append(codigo)

    totais_conferem = soma_extraidas == extraidas and soma_processadas == processadas
    periodo_confere = resultado.get("ano") == ano and resultado.get("periodo") == periodo
    completa = (
        bool(previstas)
        and status == "sucesso"
        and resultado.get("sucesso") is True
        and not erro_registrado
        and periodo_confere
        and totais_conferem
        and not any(
            (
                ausentes,
                inesperadas,
                repetidas_previstas,
                repetidas_observadas,
                falhas,
                inconsistentes,
            )
        )
    )
    return {
        "completa": completa,
        "unidades_esperadas": esperadas,
        "quantidade_esperada": len(esperadas),
        "quantidade_processada": len(recebidas),
        "ausentes": ausentes,
        "inesperadas": inesperadas,
        "duplicadas_esperadas": repetidas_previstas,
        "duplicadas_processadas": repetidas_observadas,
        "unidades_com_falha": sorted(set(falhas)),
        "contagens_inconsistentes": sorted(set(inconsistentes)),
        "sem_ofertas": sorted(set(sem_ofertas)),
        "totais_conferem": totais_conferem,
        "periodo_confere": periodo_confere,
        "ofertas_extraidas": soma_extraidas,
        "ofertas_processadas": soma_processadas,
        "erro_registrado": erro_registrado,
    }
