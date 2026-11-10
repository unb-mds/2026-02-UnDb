from app.domain.auditoria_importacao import auditar_cobertura
from app.models.importacao_execucao import ImportacaoExecucao


def auditar_registro(registro: ImportacaoExecucao) -> dict:
    relatorio = auditar_cobertura(
        registro.departamentos,
        registro.resultado_json,
        status=registro.status,
        ano=registro.ano,
        periodo=registro.periodo,
        extraidas=registro.ofertas_extraidas,
        processadas=registro.ofertas_processadas,
        erro_registrado=bool(registro.erro),
    )
    origem = registro.resultado_json.get("origem_unidades", "nao_registrada")
    return {
        "execucao": str(registro.id),
        "status": registro.status,
        "ano": registro.ano,
        "periodo": registro.periodo,
        "iniciada_em": registro.iniciada_em.isoformat(),
        "finalizada_em": registro.finalizada_em.isoformat() if registro.finalizada_em else None,
        "origem_unidades": origem,
        "cobertura_formulario_verificada": relatorio["completa"] and origem == "formulario_sigaa",
        **relatorio,
    }
