"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { unidadesDoCatalogo, urlUnidade } from "@/lib/catalogo";
import { ordenarResultados } from "@/lib/contexto-busca";
import { useCatalogo } from "@/lib/hooks/useCatalogo";
import Caminho from "./caminho";
import DisciplinaCatalogo from "./disciplina-catalogo";
import EstadoCatalogo from "./estado-catalogo";

export default function CatalogoUnidades() {
  const parametros = useSearchParams();
  const unidade = parametros.get("unidade") ?? "";
  const { consulta, tentarNovamente } = useCatalogo();
  const disciplinas = consulta?.estado === "sucesso" ? consulta.disciplinas : [];
  const unidades = unidadesDoCatalogo(disciplinas);
  const itens = ordenarResultados(unidade ? disciplinas.filter((disciplina) => disciplina.departamento === unidade) : disciplinas, "nome");
  return (
    <main className="container flex flex-1 flex-col gap-6 py-8 sm:py-12">
      <Caminho itens={[{ nome: "Início", href: "/" }, { nome: "Unidades acadêmicas" }]} />
      <div>
        <h1 className="text-3xl font-semibold">Explore qualquer unidade acadêmica</h1>
        <p className="mt-3 max-w-3xl text-sm text-(--muted)">Departamento, instituto ou faculdade, conforme o catálogo institucional de disciplinas. A consulta é pública e abrange todas as unidades disponíveis.</p>
      </div>
      {!consulta ? <EstadoCatalogo estado="carregando" tentarNovamente={tentarNovamente} />
        : consulta.estado === "erro" ? <EstadoCatalogo estado="erro" tentarNovamente={tentarNovamente} />
        : !disciplinas.length ? <EstadoCatalogo estado="vazio" tentarNovamente={tentarNovamente} /> : <>
          <nav aria-label="Unidades acadêmicas" className="flex flex-wrap gap-3">
            {["", ...unidades].map((nome) => <Link key={nome} href={nome ? urlUnidade(nome) : "/departamentos"} aria-current={unidade === nome ? "page" : undefined} className="max-w-full rounded-full border border-(--border) bg-(--panel) px-4 py-2.5 text-sm break-words text-(--muted) hover:border-accent aria-[current=page]:border-accent aria-[current=page]:bg-accent/10 aria-[current=page]:text-accent">{nome || "Todas"}</Link>)}
          </nav>
          {itens.length ? <ul aria-label="Disciplinas da unidade" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {itens.map((disciplina) => <DisciplinaCatalogo key={disciplina.id} disciplina={disciplina} />)}
          </ul> : <div className="rounded-2xl border border-(--border) bg-(--panel) p-6" role="status">
            <h2 className="text-lg font-semibold">Nenhuma disciplina encontrada nesta unidade</h2>
            <p className="mt-2 text-sm text-(--muted)">A unidade “{unidade}” não está disponível neste catálogo.</p>
            <Link href="/departamentos" className="button mt-4">Ver todas as unidades</Link>
          </div>}
        </>}
    </main>
  );
}
