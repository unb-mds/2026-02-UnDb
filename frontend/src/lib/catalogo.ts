import type { DisciplinaDetalhe } from "./types/institucional";
import { nomeUnidade } from "./unidade";

export function nomesDasUnidades(disciplinas: readonly Pick<DisciplinaDetalhe, "departamento" | "departamentoNome">[]): Map<string, string> {
  return new Map(disciplinas.map((disciplina) => [disciplina.departamento, nomeUnidade(disciplina)]));
}

/** Nomes institucionais preservados, sem inferir siglas ou unir unidades por aproximação. */
export function unidadesDoCatalogo(disciplinas: readonly DisciplinaDetalhe[]): string[] {
  const nomes = nomesDasUnidades(disciplinas);
  return [...nomes.keys()].sort((a, b) => nomes.get(a)!.localeCompare(nomes.get(b)!, "pt-BR") || a.localeCompare(b));
}

export function urlUnidade(unidade: string): string {
  return `/departamentos?${new URLSearchParams({ unidade })}`;
}
