import { catalogoPublico } from "@/lib/consultas-publicas";
import { TAMANHO_SITEMAP, urlPublica, xmlUrls } from "@/lib/seo";
export const dynamic = "force-dynamic";
export async function GET() {
  try {
    const tipos = ["professores", "disciplinas"] as const;
    const catalogos = await Promise.all(tipos.map(tipo => catalogoPublico(tipo)));
    const urls = [urlPublica("/sitemaps/paginas/0.xml")];
    catalogos.forEach((itens, i) => {
      for (let pagina = 0; pagina < Math.ceil(itens.length / TAMANHO_SITEMAP); pagina++) {
        urls.push(urlPublica(`/sitemaps/${tipos[i]}/${pagina}.xml`));
      }
    });
    return new Response(xmlUrls(urls, true), { headers: { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=0, s-maxage=3600" } });
  } catch {
    return new Response("Catálogo temporariamente indisponível.", { status: 503, headers: { "Cache-Control": "no-store", "Retry-After": "60" } });
  }
}
