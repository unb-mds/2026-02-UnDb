"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listarDestaques, type DisciplinaDestaque } from "@/lib/services/destaques";
import { nomeUnidade } from "@/lib/unidade";
import Icone from "./icone";

type Consulta = { estado: "carregando" } | { estado: "erro" } | { estado: "sucesso"; dados: DisciplinaDestaque[] };

export default function DestaquesHome() {
  const [consulta, setConsulta] = useState<Consulta>({ estado: "carregando" });
  const [tentativa, setTentativa] = useState(0);
  useEffect(() => {
    const controlador = new AbortController();
    void listarDestaques(controlador.signal).then(dados => {
      if (!controlador.signal.aborted) setConsulta({ estado: "sucesso", dados });
    }).catch(() => {
      if (!controlador.signal.aborted) setConsulta({ estado: "erro" });
    });
    return () => controlador.abort();
  }, [tentativa]);

  return <section aria-labelledby="destaques-titulo" className="flex min-w-0 flex-col gap-4">
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div><span className="kicker">Experiências compartilhadas</span><h2 id="destaques-titulo" className="section-title mt-2">Disciplinas mais avaliadas</h2></div>
      <Link href="/disciplinas" className="link text-sm">Buscar disciplina →</Link>
    </div>
    <p className="max-w-2xl text-sm leading-relaxed text-(--ink-soft)">Por quantidade de avaliações — esse volume não indica qualidade nem uma nota geral da disciplina.</p>
    {consulta.estado === "carregando" && <p role="status" className="rounded-2xl border border-(--border) p-5 text-sm text-(--muted)">Carregando disciplinas mais avaliadas…</p>}
    {consulta.estado === "erro" && <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-(--border) p-5"><p role="status" className="text-sm text-(--muted)">Não foi possível carregar as disciplinas mais avaliadas.</p><button className="button" onClick={() => { setConsulta({ estado: "carregando" }); setTentativa(v => v + 1); }}>Tentar novamente</button></div>}
    {consulta.estado === "sucesso" && (!consulta.dados.length ? <p className="rounded-2xl border border-(--border) p-5 text-sm text-(--muted)">As disciplinas aparecerão aqui quando receberem avaliações. Você já pode explorar o catálogo e contribuir.</p> : <ul aria-label="Disciplinas mais avaliadas" className="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
      {consulta.dados.map(d => <li key={d.id} className="flex min-w-0">
        <Link href={`/disciplinas/${d.id}`} className="group flex w-full min-w-0 flex-col gap-4 rounded-2xl border border-(--border) bg-(--panel) p-5 text-foreground transition-colors hover:border-accent hover:bg-(--accent-soft)">
          <div className="flex flex-wrap items-center justify-between gap-2"><span className="code-chip max-w-full [overflow-wrap:anywhere]"><span className="sr-only">Código da disciplina: </span>{d.codigo}</span><span className="text-xs text-(--muted)">{d.total_avaliacoes} {d.total_avaliacoes === 1 ? "avaliação" : "avaliações"}</span></div>
          <h3 className="text-lg leading-snug font-semibold tracking-tight [overflow-wrap:anywhere]">{d.nome}</h3>
          <p className="text-xs leading-relaxed text-(--muted) [overflow-wrap:anywhere]">{nomeUnidade(d)}</p>
          <span className="mt-auto flex items-center justify-between gap-3 border-t border-(--border) pt-4 text-sm font-medium text-accent">Comparar professores <Icone nome="arrow-right" pequeno /></span>
        </Link>
      </li>)}
    </ul>)}
  </section>;
}
