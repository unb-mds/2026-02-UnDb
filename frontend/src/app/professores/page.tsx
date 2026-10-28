import { Suspense } from "react";
import BuscaInstitucional from "@/components/busca-institucional";

export default function BuscaProfessoresPage() {
  return (
    <Suspense fallback={<p role="status" className="p-4">Carregando busca…</p>}>
      <BuscaInstitucional tipo="professores" />
    </Suspense>
  );
}
