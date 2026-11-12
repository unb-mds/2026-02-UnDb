"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { iniciaisProfessor } from "@/lib/iniciais";
import { nomeUnidade } from "@/lib/unidade";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import type { TurmaInstitucional } from "@/lib/types/institucional";
import EstrelasDidatica, { formatarDidatica } from "./estrelas-didatica";
import Icone from "./icone";

const labels = {
  FACIL: "Fácil",
  MEDIO: "Médio",
  DIFICIL: "Difícil",
  RUIM: "Ruim",
  BOM: "Bom",
} as const;

function textoAvaliacoes(total: number) {
  return `${total} ${total === 1 ? "avaliação" : "avaliações"}`;
}

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
  const trilho = useRef<HTMLUListElement>(null);
  const [limites, setLimites] = useState({ inicio: true, fim: true });

  const nomesRepetidos = new Set(
    professores
      .filter((a) =>
        professores.some(
          (b) => b.professorId !== a.professorId && b.professor.nome === a.professor.nome
        )
      )
      .map((a) => a.professor.nome)
  );

  // A API já aplica os desempates vigentes. Na ordem crescente, altere somente
  // a recomendação e preserve a ordem recebida nos empates e na insuficiência.
  const ordenados = !ascendente ? professores : [...professores].sort((a, b) => {
    if (a.dadosSuficientes !== b.dadosSuficientes) {
      return a.dadosSuficientes ? -1 : 1;
    }
    if (a.dadosSuficientes && b.dadosSuficientes && a.recomenda !== b.recomenda) {
      return a.recomenda - b.recomenda;
    }
    return 0;
  });

  useEffect(() => {
    const elemento = trilho.current;
    if (!elemento) return;
    const atualizar = () => setLimites({
      inicio: elemento.scrollLeft <= 4,
      fim: elemento.scrollLeft + elemento.clientWidth >= elemento.scrollWidth - 4,
    });
    atualizar();
    elemento.addEventListener("scroll", atualizar, { passive: true });
    const observador = new ResizeObserver(atualizar);
    observador.observe(elemento);
    return () => { elemento.removeEventListener("scroll", atualizar); observador.disconnect(); };
  }, [professores.length]);

  function rolar(direcao: 1 | -1) {
    const elemento = trilho.current;
    const cartao = elemento?.querySelector("li");
    if (!elemento || !cartao) return;
    const reduzido = matchMedia("(prefers-reduced-motion: reduce)").matches;
    elemento.scrollBy({ left: direcao * (cartao.getBoundingClientRect().width + 20), behavior: reduzido ? "auto" : "smooth" });
  }

  return (
    <section className="comparison-section glass p-5 sm:p-8" aria-labelledby="comparacao-titulo">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="max-w-2xl">
          <span className="kicker">Comparação</span>
          <h2 id="comparacao-titulo" className="section-title mt-2">Comparação de professores</h2>
          <p className="lead mt-3">
            {professores.length}{" "}
            {nomesRepetidos.size > 0
              ? "registros de professores"
              : professores.length === 1
                ? "professor"
                : "professores"}{" "}
            com oferta registrada para esta matéria. Cada cartão mostra sua própria base de respostas.
          </p>
        </div>
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

      {!professores.length ? (
        <div className="state-box mt-8">
          <p>Nenhum professor com turma ativa registrada para esta disciplina no momento.</p>
        </div>
      ) : (
        <>
          <ul
            ref={trilho}
            id="comparacao-cartoes"
            className="carousel mt-8"
            aria-label="Comparação de professores por recomendação; dados insuficientes ficam ao final"
            tabIndex={0}
          >
            {ordenados.map((a, i) => (
              <li key={a.professorId} aria-label={`${i + 1} de ${ordenados.length}: ${a.professor.nome}`}>
                <article className="pro-card">
                  <header className="pro-card-head">
                    <span className="avatar-initials" aria-hidden="true">{iniciaisProfessor(a.professor.nome)}</span>
                    <div className="min-w-0">
                      <h3 className="break-words">
                        <Link href={comContextoBusca(`/professores/${a.professorId}`, contexto)}>{a.professor.nome}</Link>
                      </h3>
                      <small className="label-mono text-[11px]!">{textoAvaliacoes(a.totalAvaliacoes)}</small>
                    </div>
                  </header>
                  <p className="-mt-2 text-xs text-(--muted)">
                    Unidade acadêmica: {nomeUnidade(a.professor)}
                    {nomesRepetidos.has(a.professor.nome) && (
                      <span className="mt-1 block font-medium text-accent">
                        {turmas
                          .filter((t) => t.professores.some((p) => p.id === a.professorId))
                          .map((t) => `Turma ${t.codigo} · ${t.semestre}`)
                          .join(" / ") || "Turma em registro separado"}
                      </span>
                    )}
                  </p>
                  {a.dadosSuficientes ? (
                    <>
                      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                        <EstrelasDidatica valor={a.didatica} />
                        <span className="text-sm text-(--ink-soft)"><strong className="text-2xl font-medium text-foreground tabular-nums">{formatarDidatica(a.didatica)}</strong> de 5 · Didática</span>
                      </div>
                      <dl className="pro-card-stats">
                        <div>
                          <dt className="label-mono">Dificuldade</dt>
                          <dd>{labels[a.dificuldade]}</dd>
                        </div>
                        <div>
                          <dt className="label-mono">Chamada</dt>
                          <dd>{a.chamada === "CONFLITANTE" ? "Conflitante" : a.chamada ? "Sim" : "Não"}</dd>
                        </div>
                        <div>
                          <dt className="label-mono">Material</dt>
                          <dd>
                            {a.disponibilizaMaterial === "CONFLITANTE"
                              ? "Conflitante"
                              : !a.disponibilizaMaterial
                                ? "Não"
                                : `Sim${a.qualidadeMaterial ? ` · ${labels[a.qualidadeMaterial]}` : ""}`}
                          </dd>
                        </div>
                      </dl>
                      <div className="pro-card-recommend">
                        <span className="label-mono">Recomendam</span>
                        <strong>{a.recomenda}%</strong>
                        <span className="meter" aria-hidden="true">
                          <span style={{ width: `${a.recomenda}%` }} />
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="state-box my-auto">
                      <strong>{a.totalAvaliacoes === 0 ? "Sem avaliações ainda" : "Dados insuficientes"}</strong>
                      <span>
                        {a.totalAvaliacoes === 0
                          ? "Isso não é uma avaliação negativa."
                          : "Mínimo de 3 avaliações para exibir os critérios."}
                      </span>
                    </div>
                  )}
                  <div className="pro-card-actions">
                    <Link
                      className="button"
                      href={comContextoBusca(`/professores/${a.professorId}/disciplinas/${disciplinaId}`, contexto)}
                    >
                      Consultar critérios <Icone nome="arrow-right" pequeno />
                    </Link>
                    <div className="pro-card-links">
                      <Link className="link" href={comContextoBusca(`/professores/${a.professorId}`, contexto)}>
                        Ver disciplinas
                      </Link>
                      <Link
                        className="link"
                        href={comContextoBusca(`/professores/${a.professorId}/disciplinas/${disciplinaId}/avaliar`, contexto)}
                      >
                        Avaliar nesta disciplina
                      </Link>
                    </div>
                  </div>
                </article>
              </li>
            ))}
          </ul>
          {!(limites.inicio && limites.fim) && (
            <div className="carousel-controls">
              <button type="button" className="carousel-arrow" aria-label="Professores anteriores" aria-controls="comparacao-cartoes" disabled={limites.inicio} onClick={() => rolar(-1)}>
                <Icone nome="arrow-left" />
              </button>
              <button type="button" className="carousel-arrow" aria-label="Próximos professores" aria-controls="comparacao-cartoes" disabled={limites.fim} onClick={() => rolar(1)}>
                <span className="inline-flex rotate-180"><Icone nome="arrow-left" /></span>
              </button>
            </div>
          )}
        </>
      )}

      <div className="note mt-8">
        <Icone nome="info" />
        <p>
          <strong>Como interpretar estes dados</strong>
          Só a recomendação ordena a comparação. Empate: mais avaliações primeiro, depois nome. Dificuldade e Chamada são informações neutras; o UnDb não cria nota geral.
        </p>
      </div>
      {nomesRepetidos.size > 0 && (
        <p className="fine-print">
          Nomes iguais aparecem separados quando a origem mantém registros distintos. Confira a turma; esses registros não foram unidos automaticamente.
        </p>
      )}
    </section>
  );
}
