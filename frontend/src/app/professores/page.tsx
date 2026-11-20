import { metadadosPagina } from "@/lib/seo";
import CatalogoLinks from "@/components/catalogo-links";
import { Suspense } from "react";
import BuscaInstitucional from "@/components/busca-institucional";

export async function generateMetadata({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const parametros = await searchParams;
  const filtrada = Object.values(parametros).some(valor => valor !== undefined && valor !== "");
  const metadata = metadadosPagina("Buscar professores da UnB | UnDb", "Encontre professores da UnB e consulte avaliações por professor e disciplina.", "/professores", !filtrada);
  if (filtrada) metadata.alternates = undefined;
  return metadata;
}

export default async function BuscaProfessoresPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const parametros = await searchParams;
  const filtrada = Object.values(parametros).some(valor => valor !== undefined && valor !== "");
  return (<main className="flex flex-1 flex-col">
    <Suspense fallback={<p role="status" className="p-4">Carregando busca…</p>}>
      <BuscaInstitucional tipo="professores" />
    </Suspense>
    {!filtrada && <CatalogoLinks tipo="professores" pagina={0} />}
  </main>);
}
