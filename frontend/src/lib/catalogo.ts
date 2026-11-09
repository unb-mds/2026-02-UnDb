import type { DisciplinaDetalhe } from "./types/institucional";

/** Nomes institucionais preservados, sem inferir siglas ou unir unidades por aproximação. */
export function unidadesDoCatalogo(disciplinas: readonly DisciplinaDetalhe[]): string[] {
  return [...new Set(disciplinas.map((disciplina) => disciplina.departamento))]
    .sort((a, b) => a.localeCompare(b, "pt-BR"));
}

export function urlUnidade(unidade: string): string {
  return `/departamentos?${new URLSearchParams({ unidade })}`;
}
