import { metadadosPagina } from "@/lib/seo";
import CatalogoLinks from "@/components/catalogo-links";
import { Suspense } from "react";
import BuscaInstitucional from "@/components/busca-institucional";

export async function generateMetadata({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const parametros = await searchParams;
  const filtrada = Object.values(parametros).some(valor => valor !== undefined && valor !== "");
  const metadata = metadadosPagina("Buscar disciplinas da UnB | UnDb", "Encontre disciplinas da UnB e consulte avaliações por professor e disciplina.", "/disciplinas", !filtrada);
  if (filtrada) metadata.alternates = undefined;
  return metadata;
}

export default async function BuscaDisciplinasPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const parametros = await searchParams;
  const filtrada = Object.values(parametros).some(valor => valor !== undefined && valor !== "");
  return (<main className="flex flex-1 flex-col">
    <Suspense fallback={<p role="status" className="p-4">Carregando busca…</p>}>
      <BuscaInstitucional tipo="disciplinas" />
    </Suspense>
    {!filtrada && <CatalogoLinks tipo="disciplinas" pagina={0} />}
  </main>);
}
