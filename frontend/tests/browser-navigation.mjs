/** CDP pode trocar o contexto entre Page.navigate e a próxima leitura do DOM. */
export function contextoEmTransicao(erro) {
  return /Execution context was destroyed|Cannot find context with specified id|Cannot find default execution context/.test(erro?.message ?? '');
}

export async function lerTextoPagina(avaliar) {
  try {
    return await avaliar("document.body?.innerText ?? ''");
  } catch (erro) {
    // Somente erros transitórios do protocolo; erros de script/produto continuam falhando.
    if (contextoEmTransicao(erro)) return '';
    throw erro;
  }
}
