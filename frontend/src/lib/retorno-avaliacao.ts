import { identificadorValido } from "./identificador";

export function caminhoAvaliacao(professorId: string, disciplinaId: string): string {
  return `/professores/${professorId}/disciplinas/${disciplinaId}/avaliar`;
}

/** Aceita somente uma rota interna válida de avaliação; nunca um destino externo. */
export function retornoAvaliacaoSeguro(valor: string | null | undefined): string | null {
  if (!valor || Array.from(valor).length > 2048 || /[\u0000-\u001f\u007f#]/.test(valor) || /%(?![\da-f]{2})/i.test(valor)) return null;
  const separador = valor.indexOf("?");
  const caminho = separador < 0 ? valor : valor.slice(0, separador);
  const query = separador < 0 ? undefined : valor.slice(separador + 1);
  const partes = caminho.match(/^\/professores\/([^/]+)\/disciplinas\/([^/]+)\/avaliar$/);
  if (!partes || partes[0] !== caminho || !identificadorValido(partes[1]) || !identificadorValido(partes[2])) return null;
  if (query !== undefined) {
    const parametros = new URLSearchParams(query);
    const chaves = [...parametros.keys()];
    if (chaves.length !== 3 || new Set(chaves).size !== 3 || chaves.some((chave) => !["busca", "q", "ordem"].includes(chave))) return null;
    if (!["professores", "disciplinas"].includes(parametros.get("busca") ?? "") || !["nome", "unidade"].includes(parametros.get("ordem") ?? "")) return null;
    if (/[\u0000-\u001f\u007f]/.test(parametros.get("q") ?? "")) return null;
  }
  return valor;
}
