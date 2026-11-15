import { notFound, permanentRedirect } from "next/navigation";
import CatalogoLinks from "@/components/catalogo-links";
import { catalogoPublico } from "@/lib/consultas-publicas";
import { metadadosPagina, TAMANHO_CATALOGO } from "@/lib/seo";
type Props = { params: Promise<{ tipo: string; pagina: string }> };
async function parametros(props: Props): Promise<{ tipo: "professores" | "disciplinas"; numero: number }> {
  const { tipo, pagina } = await props.params;
  if ((tipo !== "professores" && tipo !== "disciplinas") || !/^(0|[1-9]\d*)$/.test(pagina)) notFound();
  const numero = Number(pagina);
  if (!Number.isSafeInteger(numero)) notFound();
  if (!numero) permanentRedirect(`/${tipo}`);
  const catalogo = await catalogoPublico(tipo);
  if (numero * TAMANHO_CATALOGO >= catalogo.length) notFound();
  return { tipo, numero };
}
export async function generateMetadata(props: Props) {
  const { tipo, numero } = await parametros(props);
  return metadadosPagina(`Catálogo de ${tipo} da UnB — página ${numero + 1} | UnDb`, `Consulte ${tipo} da UnB e encontre avaliações por disciplina.`, `/catalogo/${tipo}/${numero}`);
}
export default async function Page(props: Props) {
  const { tipo, numero } = await parametros(props);
  return <main className="flex flex-1 flex-col gap-6 py-10"><h1 className="container page-title">{tipo === "professores" ? "Professores" : "Disciplinas"} da UnB</h1><CatalogoLinks tipo={tipo} pagina={numero} /></main>;
}
