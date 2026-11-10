"use client";

import Link from "next/link";
import { useState } from "react";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import type { TurmaInstitucional } from "@/lib/types/institucional";

const labels = {
  FACIL: "Fácil",
  MEDIO: "Médio",
  DIFICIL: "Difícil",
  RUIM: "Ruim",
  BOM: "Bom",
} as const;

export default function ComparacaoDark({
  professores,
  disciplinaId,
  contexto,
  turmas = [],
}: {
  professores: AvaliacaoAgregada[];
  disciplinaId: string;
  contexto: ContextoBusca | null;
  turmas?: TurmaInstitucional[];
}) {
  const [ascendente, setAscendente] = useState(false);

  const nomesRepetidos = new Set(
    professores
      .filter((a) =>
        professores.some(
          (b) => b.professorId !== a.professorId && b.professor.nome === a.professor.nome
        )
      )
      .map((a) => a.professor.nome)
  );

  const ordenados = [...professores].sort((a, b) => {
    if (a.dadosSuficientes !== b.dadosSuficientes) {
      return a.dadosSuficientes ? -1 : 1;
    }
    if (a.dadosSuficientes && b.dadosSuficientes && a.recomenda !== b.recomenda) {
      return (ascendente ? 1 : -1) * (a.recomenda - b.recomenda);
    }
    return (
      b.totalAvaliacoes - a.totalAvaliacoes ||
      a.professor.nome.localeCompare(b.professor.nome, "pt-BR")
    );
  });

  return (
    <section className="comparison-section">
      <div className="section-heading">
        <h2>Comparação de professores</h2>
        {professores.some((p) => p.dadosSuficientes) && (
          <button
            type="button"
            className="button sort"
            onClick={() => setAscendente(!ascendente)}
          >
            Ordenar por{" "}
            <strong>% de recomendação {ascendente ? "↑" : "↓"}</strong>
          </button>
        )}
      </div>

      <p className="mb-4 text-sm text-foreground/70">
        {professores.length}{" "}
        {nomesRepetidos.size > 0
          ? "registros de professores"
          : professores.length === 1
            ? "professor"
            : "professores"}{" "}
        com oferta registrada para esta matéria.
      </p>

      {!professores.length ? (
        <div className="panel p-5 text-sm text-foreground/70">
          <p>Nenhum professor com turma ativa registrada para esta disciplina no momento.</p>
        </div>
      ) : (
        <div
          className="table-scroll"
          role="region"
          aria-label="Comparação de professores; role para ver todas as colunas"
          tabIndex={0}
        >
          <table>
            <caption className="sr-only">
              Comparação de professores por recomendação. Dados insuficientes ficam ao final.
            </caption>
            <thead>
              <tr>
                {["#", "Professor", "Avaliações", "Didática", "Dificuldade", "Chamada", "Material", "Recomenda"].map(
                  (coluna) => (
                    <th key={coluna} scope="col">
                      {coluna}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {ordenados.map((a, i) => (
                <tr key={a.professorId}>
                  <td className="muted">{i + 1}</td>
                  <th scope="row">
                    <div>
                      <Link
                        className="hover:text-accent underline-offset-2 hover:underline"
                        href={comContextoBusca(`/professores/${a.professorId}`, contexto)}
                      >
                        {a.professor.nome}
                      </Link>
                    </div>
                    <span className="table-unit">
                      Unidade acadêmica: {a.professor.departamento}
                    </span>
                    {nomesRepetidos.has(a.professor.nome) && (
                      <span className="table-unit text-accent font-medium">
                        {turmas
                          .filter((t) => t.professores.some((p) => p.id === a.professorId))
                          .map((t) => `Turma ${t.codigo} · ${t.semestre}`)
                          .join(" / ") || "Turma em registro separado"}
                      </span>
                    )}
                    <div className="table-actions">
                      <Link
                        href={comContextoBusca(
                          `/professores/${a.professorId}/disciplinas/${disciplinaId}`,
                          contexto
                        )}
                      >
                        Consultar critérios
                      </Link>
                      <Link
                        href={comContextoBusca(
                          `/professores/${a.professorId}`,
                          contexto
                        )}
                      >
                        Ver disciplinas
                      </Link>
                      <Link
                        href={comContextoBusca(
                          `/professores/${a.professorId}/disciplinas/${disciplinaId}/avaliar`,
                          contexto
                        )}
                      >
                        Avaliar nesta disciplina →
                      </Link>
                    </div>
                  </th>
                  <td>{a.totalAvaliacoes}</td>
                  {a.dadosSuficientes ? (
                    <>
                      <td>
                        {a.didatica.toLocaleString("pt-BR", {
                          minimumFractionDigits: 1,
                          maximumFractionDigits: 1,
                        })}
                      </td>
                      <td>{labels[a.dificuldade]}</td>
                      <td>
                        {a.chamada === "CONFLITANTE"
                          ? "Conflitante"
                          : a.chamada
                            ? "Sim"
                            : "Não"}
                      </td>
                      <td>
                        {a.disponibilizaMaterial === "CONFLITANTE"
                          ? "Conflitante"
                          : !a.disponibilizaMaterial
                            ? "Não"
                            : `Sim${a.qualidadeMaterial ? ` · ${labels[a.qualidadeMaterial]}` : ""}`}
                      </td>
                      <td>
                        <div className="recommend">
                          <strong>{a.recomenda}%</strong>
                          <span className="bar" aria-hidden="true">
                            <span style={{ width: `${a.recomenda}%` }} />
                          </span>
                        </div>
                      </td>
                    </>
                  ) : (
                    <td colSpan={5}>
                      <div className="insufficient">
                        {a.totalAvaliacoes === 0
                          ? "Sem avaliações ainda — isso não é uma avaliação negativa"
                          : "Dados insuficientes — mínimo de 3 avaliações para exibir os critérios"}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {nomesRepetidos.size > 0 && (
        <p className="fine-print">
          Nomes iguais aparecem separados quando a origem mantém registros distintos. Confira a turma; esses registros não foram unidos automaticamente.
        </p>
      )}
      <p className="fine-print">
        Só a recomendação ordena a comparação. Empate: mais avaliações primeiro, depois nome. Dificuldade e Chamada são informações neutras.
      </p>
    </section>
  );
}
