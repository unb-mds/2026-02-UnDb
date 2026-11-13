"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/services/api-client";
import { compararProfessoresDaDisciplina } from "@/lib/services/disciplinas";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import { identificadorValido } from "@/lib/identificador";
import Link from "next/link";
import Icone from "./icone";

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
  return <section aria-labelledby="destaques-titulo" className="flex flex-col gap-5">
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div><span className="kicker">Experiências compartilhadas</span><h2 id="destaques-titulo" className="section-title mt-2">Explore as disciplinas</h2></div>
      <Link href="/disciplinas" className="link text-sm">Buscar disciplina →</Link>
    </div>
    <p className="lead">As mais avaliadas do site, pela quantidade de avaliações — sem nota geral.</p>
    <ul aria-label="Disciplinas mais avaliadas" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {dados.map(d => <li key={d.id} className="flex min-w-0">
        <Link href={`/disciplinas/${d.id}`} className="destaque w-full break-words">
          <div className="destaque-visual">
            <span className="destaque-pill">{d.codigo}</span>
            <span className="mt-auto text-sm text-(--ink-soft)">{d.total_avaliacoes} {d.total_avaliacoes === 1 ? "avaliação" : "avaliações"}</span>
            <span className="destaque-notch" aria-hidden="true"><span className="destaque-arrow"><span className="inline-flex -rotate-45"><Icone nome="arrow-right" /></span></span></span>
          </div>
          <div className="flex flex-1 flex-col gap-3 px-3">
            <h3 className="text-xl leading-tight font-semibold tracking-tight">{d.nome}</h3>
            {d.professores && <div className="grid gap-3 border-t border-(--border) pt-3">{d.professores.slice(0, 2).map(p => <div key={p.professorId} className="text-sm"><p className="text-(--ink-soft)">{p.professor.nome}</p><p className="mt-1 text-xs text-(--muted)">{p.dadosSuficientes ? `${p.didatica.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}/5 didática · ${p.recomenda}% recomendam` : "Dados insuficientes"}</p></div>)}</div>}
            <span className="mt-auto pt-2 text-sm font-medium text-accent">Comparar professores →</span>
          </div>
        </Link>
      </li>)}
    </ul>
  </section>;
}
