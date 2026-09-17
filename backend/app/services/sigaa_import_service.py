from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.turma import Turma
from app.models.unidade import Unidade
from app.domain.texto import normalizar_busca
from app.repositories import (
    disciplina_repository,
    professor_repository,
    turma_repository,
    unidade_repository,
)
from app.scrapers.sigaa_poc import Oferta, coletar_ofertas_reais


class OfertaNaoPersistivelError(ValueError):
    """A oferta contém conflito que exige reconciliação explícita."""


FONTE_SIGAA = "SIGAA"


def _identidade_provisoria(
    oferta: Oferta, unidade: Unidade, nome: str
) -> str:
    componente = oferta.componente_id or oferta.componente_codigo
    return ":".join(
        (
            FONTE_SIGAA,
            unidade.codigo,
            oferta.periodo,
            componente,
            oferta.turma_codigo,
            normalizar_busca(nome),
        )
    )


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
            identificador_externo=oferta.componente_id,
        )
    elif (
        disciplina.identificador_externo is not None
        and oferta.componente_id is not None
        and disciplina.identificador_externo != oferta.componente_id
    ):
        raise OfertaNaoPersistivelError(
            "conflito de identidade da disciplina: "
            f"codigo={oferta.componente_codigo!r}, "
            f"persistido={disciplina.identificador_externo!r}, "
            f"recebido={oferta.componente_id!r}"
        )
    else:
        disciplina.nome = oferta.componente_nome
        disciplina.nome_normalizado = normalizar_busca(oferta.componente_nome)
        disciplina.departamento = departamento
        if oferta.componente_id is not None:
            disciplina.identificador_externo = oferta.componente_id
    return disciplina


def salvar_oferta(
    db: Session,
    oferta: Oferta,
    departamento: str,
    unidade_nome: str | None = None,
) -> Turma:
    """Sincroniza uma oferta e seus zero ou vários vínculos docentes."""
    departamento = departamento.strip()
    if not departamento:
        raise OfertaNaoPersistivelError("A oferta não informa o departamento.")

    unidade = unidade_repository.get_or_create(
        db,
        fonte=FONTE_SIGAA,
        codigo=departamento,
        nome=(unidade_nome or departamento).strip(),
        identificador_externo=oferta.unidade_id,
    )

    disciplina = _get_or_create_disciplina(db, oferta, departamento)
    turma = turma_repository.get_by_identidade(
        db,
        FONTE_SIGAA,
        unidade.id,
        disciplina.id,
        oferta.periodo,
        oferta.turma_codigo,
    )
    if turma is None:
        turma = turma_repository.create(
            db,
            FONTE_SIGAA,
            unidade.id,
            disciplina.id,
            oferta.periodo,
            oferta.turma_codigo,
        )
    turma.ativa = True

    professores: list[Professor] = []
    nomes_vistos: set[str] = set()
    for nome_bruto in oferta.docentes:
        nome = " ".join(nome_bruto.split())
        nome_normalizado = normalizar_busca(nome)
        if not nome_normalizado or nome_normalizado in nomes_vistos:
            continue
        nomes_vistos.add(nome_normalizado)
        professores.append(
            professor_repository.get_or_create_provisorio(
                db,
                nome,
                departamento,
                _identidade_provisoria(oferta, unidade, nome),
            )
        )
    turma.professores = professores
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

    @property
    def estado(self) -> str:
        if self.sucesso:
            return "sucesso"
        if self.ofertas_processadas:
            return "parcial"
        return "falha"

    def to_dict(self) -> dict[str, Any]:
        return {
            "departamento": self.departamento,
            "unidade_sigaa": self.unidade_sigaa,
            "sucesso": self.sucesso,
            "estado": self.estado,
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
    ids_observados = set()
    for oferta in ofertas:
        try:
            with db.begin_nested():
                turma = salvar_oferta(
                    db,
                    oferta,
                    departamento,
                    unidade_nome=unidade_sigaa,
                )
                ids_observados.add(turma.id)
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

    if not erros:
        try:
            unidade = unidade_repository.get_by_fonte_codigo(
                db, FONTE_SIGAA, departamento
            )
            if unidade is not None:
                with db.begin_nested():
                    turma_repository.inativar_ausentes(
                        db,
                        FONTE_SIGAA,
                        unidade.id,
                        f"{ano}.{periodo}",
                        ids_observados,
                    )
        except Exception as erro:
            erros.append(
                "falha ao sincronizar ofertas ausentes: " + _mensagem_erro(erro)
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
