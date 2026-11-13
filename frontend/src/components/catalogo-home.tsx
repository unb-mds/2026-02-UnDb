"use client";

import Link from "next/link";
import { nomesDasUnidades, unidadesDoCatalogo, urlUnidade } from "@/lib/catalogo";
import { ordenarResultados } from "@/lib/contexto-busca";
import { useCatalogo } from "@/lib/hooks/useCatalogo";
import CartoesPilha from "./cartoes-pilha";
import { nomeUnidade } from "@/lib/unidade";
import EstadoCatalogo from "./estado-catalogo";

export default function CatalogoHome({ apenasUnidades = false }: { apenasUnidades?: boolean }) {
  const { consulta, tentarNovamente } = useCatalogo();
  if (!consulta) return <EstadoCatalogo estado="carregando" tentarNovamente={tentarNovamente} />;
  if (consulta.estado === "erro") return <EstadoCatalogo estado="erro" tentarNovamente={tentarNovamente} />;
  if (!consulta.disciplinas.length) return <EstadoCatalogo estado="vazio" tentarNovamente={tentarNovamente} />;
  const disciplinas = ordenarResultados(consulta.disciplinas, "nome").slice(0, 6);
  const unidades = unidadesDoCatalogo(consulta.disciplinas);
  const nomes = nomesDasUnidades(consulta.disciplinas);
  return (
    <>
      {!apenasUnidades && <section aria-labelledby="catalogo-disciplinas" className="flex flex-col gap-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div><span className="kicker">Catálogo institucional</span><h2 id="catalogo-disciplinas" className="section-title mt-2">Explore as disciplinas</h2></div>
          <Link href="/disciplinas" className="link text-sm">Buscar disciplina →</Link>
        </div>
        <p className="lead -mt-2">Uma seleção em ordem alfabética do catálogo institucional.</p>
        <CartoesPilha rotulo="Disciplinas do catálogo" itens={disciplinas.map((d) => ({ id: d.id, href: `/disciplinas/${d.id}`, codigo: d.codigo, titulo: d.nome, tags: [{ texto: nomeUnidade(d), rotulo: "Unidade acadêmica: " }], acao: "Comparar professores desta disciplina" }))} />
      </section>}
      <section aria-labelledby="catalogo-unidades" className="flex flex-col gap-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div><span className="kicker">Unidades</span><h2 id="catalogo-unidades" className="section-title mt-2">Explore qualquer unidade acadêmica</h2></div>
          <Link href="/departamentos" className="link text-sm">Ver unidades →</Link>
        </div>
        <ul className="flex flex-wrap gap-3" aria-label="Unidades do catálogo">
          {unidades.slice(0, 8).map((unidade) => <li key={unidade} className="min-w-0 max-w-full"><Link href={urlUnidade(unidade)} className="inline-block max-w-full rounded-full border border-(--border) bg-(--panel) px-4 py-2.5 text-sm break-words text-(--ink-soft) transition-colors hover:border-accent hover:text-foreground">{nomes.get(unidade)}</Link></li>)}
        </ul>
      </section>
    </>
  );
}
