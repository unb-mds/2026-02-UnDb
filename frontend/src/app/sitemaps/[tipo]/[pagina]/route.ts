import { catalogoPublico } from "@/lib/consultas-publicas";
import { TAMANHO_SITEMAP, URLS_PUBLICAS, urlPublica, xmlUrls } from "@/lib/seo";
export const dynamic = "force-dynamic";
export async function GET(_request: Request, { params }: { params: Promise<{ tipo: string; pagina: string }> }) {
  const { tipo, pagina } = await params;
  if (!/^(0|[1-9]\d*)\.xml$/.test(pagina) || !["paginas", "professores", "disciplinas"].includes(tipo)) return new Response(null, { status: 404 });
  const numero = Number(pagina.slice(0, -4));
  if (!Number.isSafeInteger(numero)) return new Response(null, { status: 404 });
  try {
    let urls: string[];
    if (tipo === "paginas") {
      if (numero !== 0) return new Response(null, { status: 404 });
      urls = URLS_PUBLICAS.map(urlPublica);
    } else {
      const itens = await catalogoPublico(tipo as "professores" | "disciplinas");
      urls = itens.slice(numero * TAMANHO_SITEMAP, (numero + 1) * TAMANHO_SITEMAP).map(item => urlPublica(`/${tipo}/${item.id}`));
      if (!urls.length) return new Response(null, { status: 404 });
    }
    return new Response(xmlUrls(urls), { headers: { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=0, s-maxage=3600" } });
  } catch {
    return new Response("Catálogo temporariamente indisponível.", { status: 503, headers: { "Cache-Control": "no-store", "Retry-After": "60" } });
  }
}
