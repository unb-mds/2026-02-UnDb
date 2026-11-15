"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/services/api-client";
import { compararProfessoresDaDisciplina } from "@/lib/services/disciplinas";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import { identificadorValido } from "@/lib/identificador";
import Link from "next/link";

const MAXIMO_DESTAQUES = 6;
type Destaque = { id: string; codigo: string; nome: string; total_avaliacoes: number; professores?: AvaliacaoAgregada[] };
function valido(v: unknown): v is Destaque {
  if (!v || typeof v !== "object") return false;
  const d = v as Record<string, unknown>;
  return typeof d.id === "string" && identificadorValido(d.id) && typeof d.nome === "string" && typeof d.codigo === "string" && Number.isInteger(d.total_avaliacoes) && Number(d.total_avaliacoes) > 0;
}
export default function DestaquesHome() {
  const [dados, setDados] = useState<Destaque[]>([]);
  useEffect(() => {
    const c = new AbortController();
    void apiClient.request<unknown>("/api/disciplinas/destaques", {}, { signal: c.signal }).then(async resposta => {
      if (!Array.isArray(resposta)) return;
      const validos = resposta.filter(valido);
      const completos = await Promise.all(validos.slice(0, MAXIMO_DESTAQUES).map(async d => ({ ...d, professores: await compararProfessoresDaDisciplina(d.id).then(v => v.professores).catch(() => undefined) })));
      if (!c.signal.aborted) setDados(completos);
    }).catch(() => {});
    return () => c.abort();
  }, []);
  if (!dados.length) return null;
  return <section aria-labelledby="destaques-titulo" className="flex min-w-0 flex-col gap-4">
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div><span className="kicker">Experiências compartilhadas</span><h2 id="destaques-titulo" className="section-title mt-2">Disciplinas mais avaliadas</h2></div>
      <Link href="/disciplinas" className="link text-sm">Buscar disciplina →</Link>
    </div>
    <p className="text-sm leading-relaxed text-(--ink-soft)">Por quantidade de avaliações — esse volume não indica qualidade nem uma nota geral da disciplina.</p>
    <ul aria-label="Disciplinas mais avaliadas" className="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
      {dados.map(d => <li key={d.id} className="flex min-w-0">
        <Link href={`/disciplinas/${d.id}`} className="group panel flex w-full min-w-0 flex-col gap-3 p-4 text-foreground sm:p-5">
          <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-2">
            <span className="code-chip max-w-full [overflow-wrap:anywhere]"><span className="sr-only">Código da disciplina: </span>{d.codigo}</span>
            <span className="text-sm text-(--ink-soft)">{d.total_avaliacoes} {d.total_avaliacoes === 1 ? "avaliação" : "avaliações"}</span>
          </div>
          <h3 className="text-lg leading-snug font-semibold tracking-tight [overflow-wrap:anywhere]">{d.nome}</h3>
          {d.professores && <div className="grid gap-3 [overflow-wrap:anywhere] border-t border-(--border) pt-3">{d.professores.slice(0, 2).map(p => <div key={p.professorId} className="text-sm"><p className="text-(--ink-soft)">{p.professor.nome}</p><p className="mt-1 text-xs text-(--muted)">{p.dadosSuficientes ? `${p.didatica.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}/5 didática · ${p.recomenda}% recomendam` : "Dados insuficientes"}</p></div>)}</div>}
          <span className="mt-auto pt-2 text-sm font-medium text-accent underline-offset-4 group-hover:underline">Comparar professores →</span>
        </Link>
      </li>)}
    </ul>
  </section>;
}
