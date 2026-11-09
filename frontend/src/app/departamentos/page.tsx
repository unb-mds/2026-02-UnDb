import { Suspense } from "react";
import CatalogoUnidades from "@/components/catalogo-unidades";

export default function DepartamentosPage() {
  return <Suspense fallback={<p role="status" className="p-4">Carregando unidades acadêmicas…</p>}><CatalogoUnidades /></Suspense>;
}
