import { Suspense } from "react";
import BuscaInstitucional from "@/components/busca-institucional";

export default function BuscaDisciplinasPage() {
  return (
    <Suspense fallback={<p role="status" className="p-4">Carregando busca…</p>}>
      <BuscaInstitucional tipo="disciplinas" />
    </Suspense>
  );
}
