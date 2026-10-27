import { identificadorValido } from "./identificador";

export function caminhoAvaliacao(professorId: string, disciplinaId: string): string {
  return `/professores/${professorId}/disciplinas/${disciplinaId}/avaliar`;
}

/** Aceita somente uma rota interna válida de avaliação; nunca um destino externo. */
export function retornoAvaliacaoSeguro(valor: string | null | undefined): string | null {
  if (!valor) return null;
  const partes = valor.match(/^\/professores\/([^/]+)\/disciplinas\/([^/]+)\/avaliar$/);
  if (!partes || partes[0] !== valor || !identificadorValido(partes[1]) || !identificadorValido(partes[2])) return null;
  return valor;
}
