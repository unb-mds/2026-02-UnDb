import Link from "next/link";
import Icone from "./icone";
import { catalogoPublico } from "@/lib/consultas-publicas";
import { TAMANHO_CATALOGO } from "@/lib/seo";
import { nomeUnidade } from "@/lib/unidade";

export default async function CatalogoLinks({ tipo, pagina }: { tipo: "professores" | "disciplinas"; pagina: number }) {
  const catalogo = await catalogoPublico(tipo).catch(() => null);
  if (!catalogo) return <p className="container py-6 text-sm text-(--muted)">O catálogo está temporariamente indisponível. Tente novamente em instantes.</p>;
  const inicio = pagina * TAMANHO_CATALOGO;
  const itens = catalogo.slice(inicio, inicio + TAMANHO_CATALOGO);
  return <section className="container min-w-0 pb-10" aria-label={`Catálogo de ${tipo}`}>
    <div className="flex flex-wrap items-end justify-between gap-4 border-t border-(--border) pt-5 sm:pt-8">
      <div><span className="kicker">Explore a UnB</span><h2 className="section-title mt-2">Catálogo de {tipo}</h2></div>
      <p className="text-sm text-(--muted)">{catalogo.length ? `${inicio + 1}–${inicio + itens.length} de ${catalogo.length}` : "Nenhum registro disponível"} · Página {pagina + 1}</p>
    </div>
    <p className="mt-3 max-w-2xl text-sm leading-relaxed text-(--ink-soft)">Explore os registros institucionais ou use a busca acima para encontrar {tipo === "professores" ? "um professor pelo nome" : "uma disciplina pelo nome ou código"}.</p>
    <ul className="my-4 grid gap-2 sm:my-6 sm:gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {itens.map(item => <li key={item.id} className="flex min-w-0">
        <Link className="group relative flex w-full min-w-0 flex-col gap-2 sm:gap-4 rounded-2xl border border-(--border) bg-(--panel) p-3 text-foreground sm:p-5 transition-colors hover:border-accent hover:bg-(--accent-soft)" href={`/${tipo}/${item.id}`}>
          <div className="flex items-start justify-between gap-3">
            {"codigo" in item ? <span className="code-chip max-w-full [overflow-wrap:anywhere]"><span className="sr-only">Código: </span>{item.codigo}</span> : <span className="hidden size-9 sm:grid shrink-0 place-items-center rounded-xl bg-(--accent-soft) text-accent"><Icone nome="user" pequeno /></span>}
            <span aria-hidden="true" className="absolute top-3 right-3 shrink-0 text-(--muted) sm:static transition-transform group-hover:translate-x-1"><Icone nome="arrow-right" pequeno /></span>
          </div>
          <h3 className="pr-6 text-sm leading-snug font-semibold sm:pr-0 sm:text-base [overflow-wrap:anywhere]">{item.nome}</h3>
          <p className="mt-auto text-xs sm:border-t sm:border-(--border) sm:pt-3 leading-relaxed text-(--muted) [overflow-wrap:anywhere]"><span className="sr-only">Unidade acadêmica: </span>{nomeUnidade(item)}</p>
          <span className="sr-only text-sm font-medium text-accent sm:not-sr-only">{tipo === "professores" ? "Ver disciplinas e avaliações" : "Comparar professores"}</span>
        </Link>
      </li>)}
    </ul>
    <nav aria-label="Páginas do catálogo" className="flex flex-wrap items-center justify-between gap-4 border-t border-(--border) pt-5">
      <span className="text-sm text-(--muted)">Página {pagina + 1} de {Math.max(1, Math.ceil(catalogo.length / TAMANHO_CATALOGO))}</span>
      <div className="flex flex-wrap gap-3">
        {pagina > 0 && <Link className="button" href={pagina === 1 ? `/${tipo}` : `/catalogo/${tipo}/${pagina - 1}`}>Página anterior</Link>}
        {(pagina + 1) * TAMANHO_CATALOGO < catalogo.length && <Link className="button" href={`/catalogo/${tipo}/${pagina + 1}`}>Próxima página</Link>}
      </div>
    </nav>
  </section>;
}
