"""Reavalia somente pendências inconclusivas; prévia por padrão, sem unir UUIDs."""

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from uuid import UUID

from app.core.database import SessionLocal
from app.repositories import identidade_docente_repository as repo
from app.scrapers.docentes import ConsultaDocentes, normalizar
from app.scrapers.sigaa_poc import Oferta
from app.services.identidade_docente_service import resolver


@dataclass(frozen=True)
class Ocorrencia:
    id: UUID
    versao: int
    professor_id: UUID
    chave: str
    nome: str
    unidade: str
    oferta: Oferta
    estado: str = "PENDENTE"
    motivo: str = "CONSULTA_INCONCLUSIVA"


def carregar(db, motivos=("CONSULTA_INCONCLUSIVA",), nomes=None, incluir_locais=False):
    """Somente ocorrências sem decisão, com oferta e componente recuperáveis."""
    itens = repo.pendencias_reavaliaveis(db, motivos, incluir_locais)
    validas, ignoradas = [], []
    for item in itens:
        if nomes and normalizar(item.nome) not in nomes:
            continue
        origem = repo.professor(db, item.professor_id)
        linhas = repo.ofertas_da_pendencia(db, item, origem.id)
        if len(linhas) != 1 or not linhas[0][1].identificador_externo:
            ignoradas.append(str(item.id))
            continue
        _, disciplina, unidade = linhas[0]
        validas.append(
            Ocorrencia(
                item.id,
                item.versao,
                item.professor_id,
                item.chave,
                item.nome,
                item.unidade,
                Oferta(
                    disciplina.codigo,
                    disciplina.nome,
                    item.turma,
                    item.periodo,
                    (item.nome,),
                    disciplina.identificador_externo,
                    unidade.identificador_externo,
                ),
                item.estado,
                item.motivo,
            )
        )
    return validas, ignoradas


def aplicar(db, item, consulta, motivos=("CONSULTA_INCONCLUSIVA",)):
    """Revalida a versão sob o mesmo lock da importação e moderação."""
    repo.bloquear(db)
    atual = repo.por_id(db, item.id)
    if (
        atual is None
        or atual.estado != item.estado
        or atual.humana
        or atual.motivo != item.motivo
        or atual.motivo not in (*motivos, "ASSOCIACAO_LOCAL")
        or atual.versao != item.versao
        or atual.professor_id != item.professor_id
        or atual.chave != item.chave
        or atual.nome != item.nome
        or atual.unidade != item.unidade
        or atual.periodo != item.oferta.periodo
        or atual.disciplina != item.oferta.componente_codigo
        or atual.turma != item.oferta.turma_codigo
    ):
        return "ALTERADA_DESDE_PREVIA"
    componente = repo.componente_disciplina(db, item.oferta.componente_codigo)
    if componente != item.oferta.componente_id:
        return "ALTERADA_DESDE_PREVIA"
    # Usa as regras existentes; não muda turmas nem move avaliações/comentários.
    resolver(db, item.nome, item.unidade, item.chave, item.oferta, consulta)
    db.flush()
    return atual.estado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--aplicar", action="store_true", help="Grava a reavaliação; não une UUIDs."
    )
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument(
        "--perfil",
        action="append",
        default=[],
        metavar="NOME=IDENTIFICADOR",
        help="Perfil público indicado manualmente, validado novamente na execução.",
    )
    args = parser.parse_args()
    perfis = {}
    for entrada in args.perfil:
        nome, separador, identificador = entrada.rpartition("=")
        if not separador or not nome.strip() or not identificador.isdigit():
            parser.error("Usar --perfil 'NOME COMPLETO=IDENTIFICADOR'.")
        perfis[normalizar(nome)] = (nome, identificador)
    motivos = ("CONSULTA_INCONCLUSIVA", "PERFIL_AUSENTE") if perfis else ("CONSULTA_INCONCLUSIVA",)
    with SessionLocal() as db:
        itens, ignoradas = carregar(db, motivos, set(perfis) if perfis else None, bool(perfis))
    consulta = ConsultaDocentes()
    for nome, identificador in perfis.values():
        # A indicação é explícita, mas não elimina outros candidatos conhecidos.
        correspondentes = [i for i in itens if normalizar(i.nome) == normalizar(nome)]
        if not correspondentes:
            continue
        consulta.consultar(nome, correspondentes[0].oferta)
        consulta.registrar_perfil(nome, identificador)
    resultados = []
    nomes_consultados = set()
    # Toda a consulta de rede precede qualquer transação de escrita.
    for n, item in enumerate(itens, 1):
        motivo, candidatos = consulta.consultar(item.nome, item.oferta)
        if motivo == "CONSULTA_INCONCLUSIVA" and normalizar(item.nome) not in nomes_consultados:
            consulta.cache.pop(normalizar(item.nome), None)
            motivo, candidatos = consulta.consultar(item.nome, item.oferta)
        nomes_consultados.add(normalizar(item.nome))
        resultados.append(
            {"id": str(item.id), "nome": item.nome, "motivo": motivo, "candidatos": candidatos}
        )
        print(f"{n}/{len(itens)}: {item.nome}: {motivo}", flush=True)
    if args.aplicar:
        for item, resultado in zip(itens, resultados, strict=True):
            with SessionLocal() as db:
                try:
                    resultado["estado"] = aplicar(db, item, consulta, motivos)
                    db.commit()
                    print(f"Gravada {item.id}: {resultado['estado']}", flush=True)
                except Exception:
                    db.rollback()
                    raise
    relatorio = {
        "modo": "aplicacao" if args.aplicar else "previa",
        "total": len(itens),
        "ignoradas_sem_oferta": ignoradas,
        "motivos": dict(Counter(r["motivo"] for r in resultados)),
        "resultados": resultados,
    }
    args.saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in relatorio.items() if k != "resultados"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
