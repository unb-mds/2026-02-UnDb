import { metadadosPagina } from "@/lib/seo";
export const metadata = metadadosPagina("Unidades acadêmicas da UnB | UnDb", "Explore professores e disciplinas por unidade acadêmica da UnB.", "/departamentos", false);
import { Suspense } from "react";
import CatalogoUnidades from "@/components/catalogo-unidades";

export default function DepartamentosPage() {
  return <Suspense fallback={<p role="status" className="p-4">Carregando unidades acadêmicas…</p>}><CatalogoUnidades /></Suspense>;
}
