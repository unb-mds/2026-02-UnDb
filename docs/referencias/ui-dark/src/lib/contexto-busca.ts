export type TipoBusca = "professores" | "disciplinas";
export type OrdemBusca = "nome" | "unidade";
export type ParametrosBusca = Record<string, string | string[] | undefined>;

export interface ContextoBusca {
  tipo: TipoBusca;
  termo: string;
  ordem: OrdemBusca;
}

export function ordemBusca(valor: unknown): OrdemBusca {
  return valor === "unidade" ? "unidade" : "nome";
}

export function lerContextoBusca(parametros: ParametrosBusca): ContextoBusca | null {
  if (parametros.busca !== "professores" && parametros.busca !== "disciplinas") return null;
  return {
    tipo: parametros.busca,
    termo: typeof parametros.q === "string" ? parametros.q : "",
    ordem: ordemBusca(parametros.ordem),
  };
}

export function urlBusca(contexto: ContextoBusca): string {
  const parametros = new URLSearchParams({ q: contexto.termo, ordem: contexto.ordem });
  return `/${contexto.tipo}?${parametros}`;
}

/** Só propaga parâmetros conhecidos; não recebe um destino de retorno arbitrário. */
export function comContextoBusca(caminho: string, contexto: ContextoBusca | null): string {
  if (!contexto) return caminho;
  const parametros = new URLSearchParams({ busca: contexto.tipo, q: contexto.termo, ordem: contexto.ordem });
  return `${caminho}?${parametros}`;
}

const colacao = new Intl.Collator("pt-BR", { sensitivity: "base" });

/** As buscas atuais retornam o conjunto completo, sem paginação no servidor. */
export function ordenarResultados<T extends { id: string; nome: string; departamento: string }>(
  resultados: readonly T[], ordem: OrdemBusca,
): T[] {
  return [...resultados].sort((a, b) =>
    (ordem === "unidade" ? colacao.compare(a.departamento, b.departamento) : 0)
    || colacao.compare(a.nome, b.nome)
    || colacao.compare(a.departamento, b.departamento)
    || a.id.localeCompare(b.id),
  );
}
