"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/services/api-client";
import { compararProfessoresDaDisciplina } from "@/lib/services/disciplinas";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import { identificadorValido } from "@/lib/identificador";
import Link from "next/link";
import Icone from "./icone";

const MAXIMO_DESTAQUES = 6;
const TONS = ["verde", "azul", "claro", "escuro"] as const;
type Destaque = { id: string; codigo: string; nome: string; total_avaliacoes: number; professores?: AvaliacaoAgregada[] };
function valido(v: unknown): v is Destaque {
  if (!v || typeof v !== "object") return false;
  const d = v as Record<string, unknown>;
  return typeof d.id === "string" && identificadorValido(d.id) && typeof d.nome === "string" && typeof d.codigo === "string" && Number.isInteger(d.total_avaliacoes) && Number(d.total_avaliacoes) > 0;
}
export default function DestaquesHome() {
  const [dados, setDados] = useState<Destaque[]>([]);
  const [passando, setPassando] = useState<number | null>(null);
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
  return <><section aria-labelledby="destaques-titulo" className="flex flex-col gap-6">
    <div><span className="kicker">Experiências compartilhadas</span><h2 id="destaques-titulo" className="section-title mt-2">Disciplinas mais avaliadas</h2><p className="lead mt-3">Ordenadas pela quantidade de respostas, sem nota geral da disciplina.</p></div>
    {/* Disposição em galeria expansível: o cartão sob o mouse cresce e os demais encolhem. */}
    <ul aria-label="Disciplinas mais avaliadas" className="destaques-flex" onMouseLeave={() => setPassando(null)}>
      {dados.map((d, i) => <li key={d.id} className="flex min-w-0" style={{ flexGrow: passando === null ? 1 : passando === i ? 2 : 0.5 }} onMouseEnter={() => setPassando(i)} onFocusCapture={() => setPassando(i)} onBlurCapture={() => setPassando(null)}>
        <Link href={`/disciplinas/${d.id}`} className="destaque w-full">
          <div className="destaque-visual" data-tom={TONS[i % TONS.length]}>
            <span className="destaque-pill">{d.codigo}</span>
            <div><strong className="block text-5xl leading-none font-semibold tracking-tight tabular-nums">{d.total_avaliacoes}</strong><span className="mt-2 block text-sm opacity-80">{d.total_avaliacoes === 1 ? "avaliação" : "avaliações"}</span></div>
            <span className="destaque-notch" aria-hidden="true"><span className="destaque-arrow"><span className="inline-flex -rotate-45"><Icone nome="arrow-right" /></span></span></span>
          </div>
          <div className="flex flex-1 flex-col gap-3 px-3">
            <h3 className="text-xl leading-tight font-semibold tracking-tight">{d.nome}</h3>
            {d.professores && <div className="grid gap-2">{d.professores.slice(0, 2).map(p => <p key={p.professorId} className="flex flex-wrap justify-between gap-x-3 text-sm"><span className="text-(--ink-soft)">{p.professor.nome} ({p.totalAvaliacoes})</span><span className="text-(--muted)">{p.dadosSuficientes ? `${p.didatica.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}/5 didática · ${p.recomenda}% recomendam` : "Dados insuficientes"}</span></p>)}</div>}
            <div className="destaque-tags mt-auto">
              {d.professores && <span className="destaque-tag">{d.professores.length} {d.professores.length === 1 ? "professor" : "professores"}</span>}
              <span className="sr-only">Comparar professores desta disciplina</span>
            </div>
          </div>
        </Link>
      </li>)}
    </ul>
  </section><hr className="border-t border-(--border)" /></>;
}
