from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.importacao_execucao import ImportacaoExecucao
from app.services.sigaa_import_service import (
    DepartamentoImportacao,
    ResultadoImportacao,
    executar_importacao,
)


def _resumir_resultado(resultado: ResultadoImportacao) -> tuple[int, int]:
    extraidas = sum(departamento.ofertas_extraidas for departamento in resultado.departamentos)
    processadas = sum(departamento.ofertas_processadas for departamento in resultado.departamentos)
    return extraidas, processadas


def executar_importacao_agendada(
    db: Session,
    departamentos: Sequence[DepartamentoImportacao]
    | Callable[[], Sequence[DepartamentoImportacao]],
    *,
    ano: str,
    periodo: str,
    origem_unidades: str = "lista_explicita",
) -> ImportacaoExecucao:
    registro = ImportacaoExecucao(
        status="em_andamento",
        ano=ano,
        periodo=periodo,
        departamentos=[],
        ofertas_extraidas=0,
        ofertas_processadas=0,
        resultado_json={"origem_unidades": origem_unidades},
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    try:
        solicitacoes = departamentos() if callable(departamentos) else departamentos
        registro.departamentos = [
            {
                "departamento": item.departamento,
                "unidade_sigaa": item.unidade_sigaa,
            }
            for item in solicitacoes
        ]
        # Preserva o denominador mesmo se o processo for interrompido durante a coleta.
        db.commit()
        resultado = executar_importacao(
            db,
            solicitacoes,
            ano=ano,
            periodo=periodo,
        )

        extraidas, processadas = _resumir_resultado(resultado)

        registro.status = "sucesso" if resultado.sucesso else "falha"
        registro.finalizada_em = datetime.now(UTC)
        registro.ofertas_extraidas = extraidas
        registro.ofertas_processadas = processadas
        registro.resultado_json = {**resultado.to_dict(), "origem_unidades": origem_unidades}

        if resultado.sucesso:
            registro.erro = None
        else:
            erros = [
                erro for departamento in resultado.departamentos for erro in departamento.erros
            ]
            registro.erro = "\n".join(erros) or "A importação falhou."

        db.commit()
        db.refresh(registro)
        return registro

    except Exception as erro:
        db.rollback()

        registro.status = "falha"
        registro.finalizada_em = datetime.now(UTC)
        registro.erro = f"{type(erro).__name__}: {erro}"
        registro.resultado_json = {
            "origem_unidades": origem_unidades,
            "sucesso": False,
            "ano": ano,
            "periodo": periodo,
            "erro": registro.erro,
        }

        db.commit()
        db.refresh(registro)
        return registro
