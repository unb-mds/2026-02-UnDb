"use client";

import Form from "next/form";
import { useState } from "react";
import type { TipoBusca } from "@/lib/contexto-busca";

export default function BuscaEntrada() {
  const [tipo, setTipo] = useState<TipoBusca>("disciplinas");
  return (
    <Form action={`/${tipo}`} className="flex flex-col gap-4 rounded-xl border border-foreground/10 bg-foreground/[0.02] p-5">
      <fieldset className="flex flex-wrap gap-4">
        <legend className="mb-2 text-sm font-medium">Buscar por</legend>
        <label className="flex items-center gap-2"><input type="radio" name="busca" value="professores" checked={tipo === "professores"} onChange={() => setTipo("professores")} />Professor</label>
        <label className="flex items-center gap-2"><input type="radio" name="busca" value="disciplinas" checked={tipo === "disciplinas"} onChange={() => setTipo("disciplinas")} />Disciplina</label>
      </fieldset>
      <label className="flex flex-col gap-2">
        <span className="text-sm font-medium">{tipo === "professores" ? "Nome do professor" : "Nome ou código da disciplina"}</span>
        <input type="search" name="q" required minLength={2} aria-describedby="busca-entrada-ajuda"
          placeholder={tipo === "professores" ? "Nome completo ou parcial" : "Nome ou código institucional"}
          className="min-w-0 w-full rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base" />
      </label>
      <input type="hidden" name="ordem" value="nome" />
      <p id="busca-entrada-ajuda" className="text-sm text-foreground/70">Informe ao menos 2 caracteres. Você pode buscar em qualquer unidade acadêmica.</p>
      <button type="submit" className="self-start rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-on-accent hover:opacity-90">Buscar</button>
    </Form>
  );
}
