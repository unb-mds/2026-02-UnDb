from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.avaliacoes import (
    AvaliacaoParaAgregacao,
    Dificuldade,
    QualidadeMaterial,
    ResultadoAgregado,
    agregar_avaliacoes,
)
from app.models.avaliacao import Avaliacao
from app.models.usuario import Usuario
from app.repositories import (
    avaliacao_repository,
    comentario_repository,
    professor_repository,
    turma_repository,
)
from app.schemas.avaliacao import AvaliacaoCreate


MIN_AVALIACOES_EXIBICAO = 3


class RecursoNaoEncontradoError(Exception):
    pass


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _persistir_avaliacao(
    db: Session,
    usuario: Usuario,
    dados: AvaliacaoCreate,
) -> Avaliacao:
    return avaliacao_repository.salvar_ou_substituir(
        db,
        usuario_id=usuario.id,
        professor_id=dados.professor_id,
        disciplina_id=dados.disciplina_id,
        didatica=dados.didatica,
        dificuldade=dados.dificuldade,
        chamada=dados.chamada,
        disponibiliza_material=dados.disponibiliza_material,
        qualidade_material=dados.qualidade_material,
        recomenda=dados.recomenda,
        atualizado_em=_agora_utc(),
    )


def _criar_ou_substituir_comentario(
    db: Session, avaliacao_id: UUID, texto: str | None
) -> None:
    """Cria uma nova versao PENDENTE do comentario, se texto for valido.

    - texto None: mantem comentario existente (re-envio de criterios).
    - texto invalido (0/501+): nada acontece, avaliacao continua valida.
    - texto valido: remove PENDENTE anterior e cria novo apontando ao
      PUBLICADO atual (se houver), preservando o texto publicado.
    """
    if texto is None:
        return

    pendente = comentario_repository.obter_pendente_por_avaliacao(
        db, avaliacao_id
    )
    if pendente is not None:
        db.delete(pendente)

    publicado = comentario_repository.obter_publicado_por_avaliacao(
        db, avaliacao_id
    )
    substitui_id = publicado.id if publicado is not None else None

    comentario_repository.criar(
        db, avaliacao_id=avaliacao_id, texto=texto, substitui_id=substitui_id
    )


def registrar_avaliacao(
    db: Session,
    usuario: Usuario,
    dados: AvaliacaoCreate,
) -> Avaliacao:
    if avaliacao_repository.obter_professor(db, dados.professor_id) is None:
        raise RecursoNaoEncontradoError("professor nao encontrado")
    if avaliacao_repository.obter_disciplina(db, dados.disciplina_id) is None:
        raise RecursoNaoEncontradoError("disciplina nao encontrada")
    if not turma_repository.existe_vinculo_professor_disciplina(
        db, dados.professor_id, dados.disciplina_id
    ):
        raise RecursoNaoEncontradoError(
            "professor nao possui vinculo com a disciplina"
        )

    try:
        avaliacao = _persistir_avaliacao(db, usuario, dados)
        _criar_ou_substituir_comentario(db, avaliacao.id, dados.comentario)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(avaliacao)
    return avaliacao


@dataclass(frozen=True)
class ProfessorInstitucional:
    id: UUID
    nome: str
    departamento: str


@dataclass(frozen=True)
class DisciplinaInstitucional:
    id: UUID
    codigo: str
    nome: str
    departamento: str


@dataclass(frozen=True)
class ConsultaAgregada:
    professor_id: UUID
    disciplina_id: UUID
    professor: ProfessorInstitucional
    disciplina: DisciplinaInstitucional
    total_avaliacoes: int
    dados_suficientes: bool
    criterios: ResultadoAgregado | None = None


@dataclass(frozen=True)
class ComparacaoProfessores:
    disciplina: DisciplinaInstitucional
    professores: list[ConsultaAgregada]


def consultar_agregado(
    db: Session,
    professor_id: UUID,
    disciplina_id: UUID,
) -> ConsultaAgregada:
    professor = avaliacao_repository.obter_professor(db, professor_id)
    if professor is None:
        raise RecursoNaoEncontradoError("professor nao encontrado")
    disciplina = avaliacao_repository.obter_disciplina(db, disciplina_id)
    if disciplina is None:
        raise RecursoNaoEncontradoError("disciplina nao encontrada")
    if not turma_repository.existe_vinculo_professor_disciplina(
        db, professor_id, disciplina_id
    ):
        raise RecursoNaoEncontradoError(
            "professor nao possui vinculo com a disciplina"
        )

    professor_institucional = ProfessorInstitucional(
        id=professor.id,
        nome=professor.nome,
        departamento=professor.departamento,
    )
    disciplina_institucional = DisciplinaInstitucional(
        id=disciplina.id,
        codigo=disciplina.codigo,
        nome=disciplina.nome,
        departamento=disciplina.departamento,
    )

    registros = avaliacao_repository.listar_por_professor_e_disciplina(
        db,
        professor_id,
        disciplina_id,
    )
    total = len(registros)
    if total < MIN_AVALIACOES_EXIBICAO:
        return ConsultaAgregada(
            professor_id=professor_id,
            disciplina_id=disciplina_id,
            professor=professor_institucional,
            disciplina=disciplina_institucional,
            total_avaliacoes=total,
            dados_suficientes=False,
        )

    criterios = agregar_avaliacoes(
        [
            AvaliacaoParaAgregacao(
                didatica=registro.didatica,
                dificuldade=Dificuldade(registro.dificuldade.value),
                chamada=registro.chamada,
                disponibiliza_material=registro.disponibiliza_material,
                qualidade_material=(
                    QualidadeMaterial(registro.qualidade_material.value)
                    if registro.qualidade_material is not None
                    else None
                ),
                recomenda=registro.recomenda,
            )
            for registro in registros
        ]
    )
    return ConsultaAgregada(
        professor_id=professor_id,
        disciplina_id=disciplina_id,
        professor=professor_institucional,
        disciplina=disciplina_institucional,
        total_avaliacoes=total,
        dados_suficientes=True,
        criterios=criterios,
    )


def _ordenar_comparacao(
    comparacao: list["ConsultaAgregada"],
    ordenar_por: Literal["recomendacao"],
) -> list["ConsultaAgregada"]:
    if ordenar_por != "recomendacao":
        raise ValueError("ordenar_por inválido")

    return sorted(
        comparacao,
        key=lambda resultado: (
            not resultado.dados_suficientes,
            -(resultado.criterios.recomenda if resultado.criterios else 0),
            -resultado.total_avaliacoes,
            resultado.professor.nome.casefold(),
        ),
    )


def comparar_professores(
    db: Session,
    disciplina_id: UUID,
    ordenar_por: Literal["recomendacao"] = "recomendacao",
) -> ComparacaoProfessores:
    disciplina = avaliacao_repository.obter_disciplina(db, disciplina_id)
    if disciplina is None:
        raise RecursoNaoEncontradoError("disciplina nao encontrada")

    disciplina_institucional = DisciplinaInstitucional(
        id=disciplina.id,
        codigo=disciplina.codigo,
        nome=disciplina.nome,
        departamento=disciplina.departamento,
    )
    comparacao = [
        consultar_agregado(db, professor.id, disciplina_id)
        for professor in professor_repository.listar_por_disciplina(db, disciplina_id)
    ]
    comparacao_ordenada = _ordenar_comparacao(comparacao, ordenar_por)
    return ComparacaoProfessores(
        disciplina=disciplina_institucional,
        professores=comparacao_ordenada,
    )
