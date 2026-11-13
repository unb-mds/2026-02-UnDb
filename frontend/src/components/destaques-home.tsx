"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/services/api-client";
import { compararProfessoresDaDisciplina } from "@/lib/services/disciplinas";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import { identificadorValido } from "@/lib/identificador";
import Icone from "./icone";

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
      if (!Array.isArray(resposta) || !resposta.every(valido)) return;
      const completos = await Promise.all(resposta.slice(0, 6).map(async d => ({ ...d, professores: await compararProfessoresDaDisciplina(d.id).then(v => v.professores).catch(() => undefined) })));
      if (!c.signal.aborted) setDados(completos);
    }).catch(() => {});
    return () => c.abort();
  }, []);
  if (!dados.length) return null;
  return <section aria-labelledby="destaques-titulo" className="flex flex-col gap-5"><div><span className="kicker">Experiências compartilhadas</span><h2 id="destaques-titulo" className="section-title mt-2">Disciplinas com mais avaliações</h2><p className="lead mt-3">Ordenadas pela quantidade de respostas, sem nota geral da disciplina.</p></div><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{dados.map(d => <Link href={`/disciplinas/${d.id}`} key={d.id} className="tile flex flex-col gap-4 bg-linear-to-br! from-(--surface-accent)/50 to-(--success-soft)/30 p-5"><div className="flex items-center justify-between gap-3"><span className="text-accent"><Icone nome="book" /></span><div className="text-right"><span className="code-chip">{d.codigo}</span><span className="mt-2 block text-xs text-(--muted)">{d.total_avaliacoes} avaliações</span></div></div><h3 className="text-lg font-medium">{d.nome}</h3>{d.professores && <div className="grid gap-3 border-y border-(--border) py-3">{d.professores.slice(0, 2).map(p => <div key={p.professorId} className="flex flex-wrap justify-between gap-2 text-xs"><span className="text-(--ink-soft)">{p.professor.nome} ({p.totalAvaliacoes})</span><span className="text-(--muted)">{p.dadosSuficientes ? `${p.didatica.toLocaleString("pt-BR", {minimumFractionDigits:1,maximumFractionDigits:1})}/5 didática · ${p.recomenda}% recomendam` : "Dados insuficientes"}</span></div>)}</div>}<span className="mt-auto text-sm text-accent">Comparar professores →</span></Link>)}</div></section>;
}
