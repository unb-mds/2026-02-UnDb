"use client";

import { useFormStatus } from "react-dom";
import Icone from "./icone";

export default function BotaoBuscar({ compacto }: { compacto: boolean }) {
  const { pending } = useFormStatus();
  return <button type="submit" className="button primary search-submit" disabled={pending} aria-label={pending ? "Buscando…" : "Buscar"}>
    <span role="status">{pending ? "Buscando…" : "Buscar"}</span>
    {!compacto && <span aria-hidden="true" className={pending ? "search-progress" : "search-arrow"}><Icone nome={pending ? "search" : "arrow-right"} pequeno /></span>}
  </button>;
}
