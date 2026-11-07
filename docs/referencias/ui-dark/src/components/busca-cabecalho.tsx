"use client";

import Form from "next/form";
import { usePathname, useSearchParams } from "next/navigation";

export default function BuscaCabecalho() {
  const caminho = usePathname();
  const parametros = useSearchParams();
  const tipo = caminho.startsWith("/professores") || parametros.get("busca") === "professores" ? "professores" : "disciplinas";
  const termo = parametros.get("q") ?? "";
  return <Form action="/busca" className="search search-header" role="search" key={`${tipo}:${termo}`}>
    <label className="sr-only" htmlFor="cabecalho-tipo">Buscar por</label>
    <select name="busca" id="cabecalho-tipo" defaultValue={tipo}><option value="disciplinas">Disciplina</option><option value="professores">Professor</option></select>
    <label className="sr-only" htmlFor="cabecalho-termo">Buscar professor, disciplina ou código</label>
    <input name="q" id="cabecalho-termo" type="search" required minLength={2} defaultValue={termo} placeholder="Buscar professor, disciplina ou código" />
    <input name="ordem" type="hidden" value="nome" />
    <button type="submit" className="search-submit" aria-label="Buscar"><span className="search-icon" aria-hidden="true" /></button>
  </Form>;
}
