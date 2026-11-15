import Link from "next/link";
import { catalogoPublico } from "@/lib/consultas-publicas";
import { TAMANHO_CATALOGO } from "@/lib/seo";

export default async function CatalogoLinks({ tipo, pagina }: { tipo: "professores" | "disciplinas"; pagina: number }) {
  const catalogo = await catalogoPublico(tipo).catch(() => null);
  if (!catalogo) return <p className="container py-6 text-sm text-(--muted)">O catálogo está temporariamente indisponível. Tente novamente em instantes.</p>;
  const itens = catalogo.slice(pagina * TAMANHO_CATALOGO, (pagina + 1) * TAMANHO_CATALOGO);
  return <section className="container min-w-0 pb-10" aria-label={`Catálogo de ${tipo}`}>
    <h2 className="section-title">Catálogo de {tipo}</h2>
    <p className="mt-2 text-sm text-(--muted)">Página {pagina + 1} · {catalogo.length} registros. Use a busca para encontrar um nome específico.</p>
    <ul className="my-5 grid gap-3 sm:grid-cols-2">{itens.map(item => <li key={item.id} className="min-w-0"><Link className="link break-words" href={`/${tipo}/${item.id}`}>{"codigo" in item ? `${item.codigo} — ` : ""}{item.nome}</Link></li>)}</ul>
    <nav aria-label="Páginas do catálogo" className="flex flex-wrap gap-4">
      {pagina > 0 && <Link className="button" href={pagina === 1 ? `/${tipo}` : `/catalogo/${tipo}/${pagina - 1}`}>Página anterior</Link>}
      {(pagina + 1) * TAMANHO_CATALOGO < catalogo.length && <Link className="button" href={`/catalogo/${tipo}/${pagina + 1}`}>Próxima página</Link>}
    </nav>
  </section>;
}
