import { identificadorValido } from "./identificador";

const CHAVE_RETORNO_AVALIACAO = "undb:retorno-avaliacao";

export function caminhoAvaliacao(professorId: string, disciplinaId: string): string {
  return `/professores/${professorId}/disciplinas/${disciplinaId}/avaliar`;
}

/** Aceita somente uma rota interna válida de avaliação; nunca um destino externo. */
export function retornoAvaliacaoSeguro(valor: string | null | undefined): string | null {
  if (!valor) return null;
  try {
    const url = new URL(valor, "http://undb.local");
    if (url.origin !== "http://undb.local" || url.search || url.hash) return null;
    const partes = url.pathname.match(/^\/professores\/([^/]+)\/disciplinas\/([^/]+)\/avaliar$/);
    if (!partes || !identificadorValido(partes[1]) || !identificadorValido(partes[2])) return null;
    return url.pathname;
  } catch {
    return null;
  }
}

export function salvarRetornoAvaliacao(valor: string | null): void {
  if (typeof window === "undefined") return;
  const retorno = retornoAvaliacaoSeguro(valor);
  try {
    if (retorno) window.localStorage.setItem(CHAVE_RETORNO_AVALIACAO, retorno);
    else window.localStorage.removeItem(CHAVE_RETORNO_AVALIACAO);
  } catch {
    // O retorno é um refinamento; restrições do navegador não podem bloquear autenticação.
  }
}

export function lerRetornoAvaliacaoSalvo(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const salvo = retornoAvaliacaoSeguro(window.localStorage.getItem(CHAVE_RETORNO_AVALIACAO));
    if (!salvo) window.localStorage.removeItem(CHAVE_RETORNO_AVALIACAO);
    return salvo;
  } catch {
    return null;
  }
}

export function limparRetornoAvaliacaoSalvo(): void {
  try {
    if (typeof window !== "undefined") window.localStorage.removeItem(CHAVE_RETORNO_AVALIACAO);
  } catch {
    // A navegação para a avaliação continua válida se o armazenamento estiver indisponível.
  }
}
