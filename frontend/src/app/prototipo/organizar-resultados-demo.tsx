"use client";

import { useTransition } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function OrganizarResultadosDemo({ ordem, tipo }: { ordem: string; tipo: string }) {
  const router = useRouter();
  const consulta = useSearchParams();
  const [atualizando, iniciarTransicao] = useTransition();

  function organizar(valor: string) {
    const parametros = new URLSearchParams(consulta.toString());
    parametros.set("ordemBusca", valor);
    iniciarTransicao(() => router.replace(`/prototipo?${parametros}`, { scroll: false }));
  }

  return <div className="flex max-w-2xl flex-col gap-2 rounded-lg bg-foreground/[0.03] p-4">
    <label className="flex flex-col gap-2">
      <span className="text-sm font-medium">Ordenar resultados</span>
      <select name="ordemResultados" value={ordem} disabled={atualizando} onChange={(evento) => organizar(evento.target.value)} aria-describedby="ordem-resultados-ajuda"
        className="w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5 disabled:opacity-60">
        <option value="nome">{tipo === "professor" ? "Nome do professor (A–Z)" : "Nome da disciplina (A–Z)"}</option>
        <option value="departamento">Unidade acadêmica (A–Z)</option>
      </select>
    </label>
    <p id="ordem-resultados-ajuda" className="text-sm text-foreground/70">Unidade acadêmica é o departamento, instituto ou faculdade responsável. Ao trocar a opção, a lista se reorganiza sem precisar buscar novamente.</p>
    <span role="status" className="text-sm text-foreground/70">{atualizando ? "Reorganizando resultados…" : "Lista atualizada."}</span>
  </div>;
}
