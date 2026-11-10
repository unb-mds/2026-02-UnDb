type UnidadeInstitucional = { departamento: string; departamentoNome?: string | null };

/** Usa o nome da origem; o código permanece disponível para identidade e filtros. */
export function nomeUnidade(unidade: UnidadeInstitucional): string {
  const nome = unidade.departamentoNome?.trim();
  return nome && !/^\d+$/.test(nome) ? nome
    : (/^\d+$/.test(unidade.departamento) ? `Unidade ${unidade.departamento}` : unidade.departamento);
}
