"use client";

import Link from "next/link";
import { unidadesDoCatalogo, urlUnidade } from "@/lib/catalogo";
import { ordenarResultados } from "@/lib/contexto-busca";
import { useCatalogo } from "@/lib/hooks/useCatalogo";
import DisciplinaCatalogo from "./disciplina-catalogo";
import EstadoCatalogo from "./estado-catalogo";

export default function CatalogoHome() {
  const { consulta, tentarNovamente } = useCatalogo();
  if (!consulta) return <EstadoCatalogo estado="carregando" tentarNovamente={tentarNovamente} />;
  if (consulta.estado === "erro") return <EstadoCatalogo estado="erro" tentarNovamente={tentarNovamente} />;
  if (!consulta.disciplinas.length) return <EstadoCatalogo estado="vazio" tentarNovamente={tentarNovamente} />;
  const disciplinas = ordenarResultados(consulta.disciplinas, "nome").slice(0, 6);
  const unidades = unidadesDoCatalogo(consulta.disciplinas);
  return (
    <>
      <section aria-labelledby="catalogo-disciplinas" className="flex flex-col gap-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 id="catalogo-disciplinas" className="border-l-4 border-accent pl-3 text-2xl font-semibold">Explore as disciplinas</h2>
          <Link href="/disciplinas" className="text-sm text-accent hover:underline">Buscar disciplina →</Link>
        </div>
        <p className="text-sm text-(--muted)">Uma seleção em ordem alfabética do catálogo institucional.</p>
        <ul aria-label="Disciplinas do catálogo" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {disciplinas.map((disciplina) => <DisciplinaCatalogo key={disciplina.id} disciplina={disciplina} titulo="h3" />)}
        </ul>
      </section>
      <section aria-labelledby="catalogo-unidades" className="flex flex-col gap-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 id="catalogo-unidades" className="border-l-4 border-accent pl-3 text-2xl font-semibold">Explore qualquer unidade acadêmica</h2>
          <Link href="/departamentos" className="text-sm text-accent hover:underline">Ver unidades →</Link>
        </div>
        <ul className="flex flex-wrap gap-3" aria-label="Unidades do catálogo">
          {unidades.slice(0, 8).map((unidade) => <li key={unidade} className="min-w-0 max-w-full"><Link href={urlUnidade(unidade)} className="inline-block max-w-full rounded-full border border-(--border) bg-(--panel) px-4 py-2.5 text-sm break-words text-(--muted) hover:border-accent hover:text-foreground">{unidade}</Link></li>)}
        </ul>
      </section>
    </>
  );
}
