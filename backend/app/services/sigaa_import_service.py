from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.turma import Turma
from app.repositories import (
    disciplina_repository,
    professor_repository,
    turma_repository,
)
from app.scrapers.sigaa_poc import Oferta, coletar_ofertas_reais


class OfertaNaoPersistivelError(ValueError):
    """A oferta depende de informação que o modelo ainda não representa."""


def _get_or_create_professor(
    db: Session, nome: str, departamento: str
) -> Professor:
    professor = professor_repository.get_by_nome_e_departamento(
        db, nome, departamento
    )
    if professor is None:
        professor = professor_repository.create(db, nome, departamento)
    return professor


def _get_or_create_disciplina(
    db: Session, oferta: Oferta, departamento: str
) -> Disciplina:
    disciplina = disciplina_repository.get_by_codigo(db, oferta.componente_codigo)
    if disciplina is None:
        disciplina = disciplina_repository.create(
            db,
            codigo=oferta.componente_codigo,
            nome=oferta.componente_nome,
            departamento=departamento,
        )
    return disciplina


def salvar_oferta(db: Session, oferta: Oferta, departamento: str) -> Turma:
    """Persiste uma oferta cujo vínculo cabe no modelo relacional atual.

    Ofertas sem docente ou com múltiplos docentes permanecem pendentes de decisão
    de modelo na Issue #25 e são recusadas antes de qualquer escrita.
    """
    departamento = departamento.strip()
    if not departamento:
        raise OfertaNaoPersistivelError("A oferta não informa o departamento.")
    if len(oferta.docentes) != 1 or not oferta.docentes[0].strip():
        raise OfertaNaoPersistivelError(
            "A oferta deve possuir exatamente um docente para o modelo atual; "
            f"turma {oferta.turma_codigo!r} possui {len(oferta.docentes)}."
        )

    disciplina = _get_or_create_disciplina(db, oferta, departamento)
    professor = _get_or_create_professor(
        db, oferta.docentes[0].strip(), departamento
    )

    turma = turma_repository.get_by_disciplina_professor_semestre(
        db, disciplina.id, professor.id, oferta.periodo
    )
    if turma is None:
        turma = turma_repository.create(
            db, disciplina.id, professor.id, oferta.periodo
        )
    return turma


@dataclass(frozen=True)
class DepartamentoImportacao:
    departamento: str
    unidade_sigaa: str


@dataclass(frozen=True)
class ResultadoDepartamento:
    departamento: str
    unidade_sigaa: str
    sucesso: bool
    total_reportado: int | None
    ofertas_extraidas: int
    ofertas_processadas: int
    erros: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "departamento": self.departamento,
            "unidade_sigaa": self.unidade_sigaa,
            "sucesso": self.sucesso,
            "total_reportado": self.total_reportado,
            "ofertas_extraidas": self.ofertas_extraidas,
            "ofertas_processadas": self.ofertas_processadas,
            "erros": list(self.erros),
        }


@dataclass(frozen=True)
class ResultadoImportacao:
    sucesso: bool
    ano: str
    periodo: str
    inicio: datetime
    fim: datetime
    departamentos: tuple[ResultadoDepartamento, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sucesso": self.sucesso,
            "ano": self.ano,
            "periodo": self.periodo,
            "inicio": self.inicio.isoformat(),
            "fim": self.fim.isoformat(),
            "departamentos": [item.to_dict() for item in self.departamentos],
        }


ColetorOfertas = Callable[[str, str, str], tuple[list[Oferta], int | None]]


def _mensagem_erro(erro: Exception) -> str:
    detalhe = str(erro).strip()
    return f"{type(erro).__name__}: {detalhe}" if detalhe else type(erro).__name__


def _rollback_seguro(db: Session) -> str | None:
    try:
        db.rollback()
    except Exception as erro:
        return f"falha adicional no rollback: {_mensagem_erro(erro)}"
    return None


def _importar_departamento(
    db: Session,
    solicitacao: DepartamentoImportacao,
    ano: str,
    periodo: str,
    coletor: ColetorOfertas,
) -> ResultadoDepartamento:
    departamento = solicitacao.departamento.strip()
    unidade_sigaa = solicitacao.unidade_sigaa.strip()
    if not departamento or not unidade_sigaa:
        return ResultadoDepartamento(
            departamento=departamento,
            unidade_sigaa=unidade_sigaa,
            sucesso=False,
            total_reportado=None,
            ofertas_extraidas=0,
            ofertas_processadas=0,
            erros=("departamento e unidade SIGAA sao obrigatorios",),
        )

    try:
        ofertas, total_reportado = coletor(unidade_sigaa, ano, periodo)
    except Exception as erro:
        return ResultadoDepartamento(
            departamento=departamento,
            unidade_sigaa=unidade_sigaa,
            sucesso=False,
            total_reportado=None,
            ofertas_extraidas=0,
            ofertas_processadas=0,
            erros=(_mensagem_erro(erro),),
        )

    erros: list[str] = []
    processadas = 0
    for oferta in ofertas:
        try:
            with db.begin_nested():
                salvar_oferta(db, oferta, departamento)
            processadas += 1
        except Exception as erro:
            erros.append(
                f"turma {oferta.turma_codigo!r} de "
                f"{oferta.componente_codigo!r}: {_mensagem_erro(erro)}"
            )

    if total_reportado is None:
        erros.append(
            "total de ofertas nao informado pelo SIGAA; "
            "nao foi possivel validar a extracao"
        )
    elif total_reportado != len(ofertas):
        erros.append(
            "total informado pelo SIGAA diverge da extracao: "
            f"reportado={total_reportado}, extraido={len(ofertas)}"
        )

    try:
        db.commit()
    except Exception as erro:
        erros.append(f"falha ao confirmar persistencia: {_mensagem_erro(erro)}")
        erro_rollback = _rollback_seguro(db)
        if erro_rollback is not None:
            erros.append(erro_rollback)
        processadas = 0

    return ResultadoDepartamento(
        departamento=departamento,
        unidade_sigaa=unidade_sigaa,
        sucesso=not erros,
        total_reportado=total_reportado,
        ofertas_extraidas=len(ofertas),
        ofertas_processadas=processadas,
        erros=tuple(erros),
    )


def executar_importacao(
    db: Session,
    departamentos: Sequence[DepartamentoImportacao],
    ano: str,
    periodo: str,
    coletor: ColetorOfertas = coletar_ofertas_reais,
) -> ResultadoImportacao:
    """Coleta e persiste unidades isoladamente, retornando o contrato do RF19.

    A funcao nunca propaga falha de uma unidade para a seguinte. O chamador recebe
    um resultado estruturado que pode ser registrado ou agendado pela Issue #26.
    """
    if not departamentos:
        raise ValueError("ao menos um departamento deve ser informado")

    inicio = datetime.now(UTC)
    resultados = tuple(
        _importar_departamento(db, item, ano, periodo, coletor)
        for item in departamentos
    )
    fim = datetime.now(UTC)
    return ResultadoImportacao(
        sucesso=all(item.sucesso for item in resultados),
        ano=ano,
        periodo=periodo,
        inicio=inicio,
        fim=fim,
        departamentos=resultados,
    )
