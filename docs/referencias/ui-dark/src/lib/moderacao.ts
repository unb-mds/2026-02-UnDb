import { ApiError } from "./services/http-error";
import type { AcaoModeracao, EstadoComentario, MotivoDenuncia } from "./types/moderacao";

export const rotulosEstado: Record<EstadoComentario, string> = {
  PENDENTE: "Pendente de aprovação", PUBLICADO: "Publicado", SUSPENSO: "Suspenso",
  REMOVIDO: "Removido", RETIRADO: "Retirado pelo autor", SUBSTITUIDO: "Substituído", REJEITADO: "Rejeitado",
};
export const rotulosAcao: Record<AcaoModeracao, string> = {
  APROVAR: "Aprovar", REJEITAR: "Rejeitar", MANTER: "Manter publicado", RESTAURAR: "Restaurar publicação", REMOVER: "Remover da publicação",
};
export const rotulosMotivo: Record<MotivoDenuncia, string> = {
  OFENSA_PESSOAL: "Ofensa pessoal", XINGAMENTO: "Xingamento", PALAVRAO: "Palavrão", AMEACA: "Ameaça",
  DISCRIMINACAO: "Discriminação", EXPOSICAO_DADOS_PESSOAIS: "Exposição de dados pessoais", SPAM: "Spam",
};

/** Apresenta as transições do contrato; autorização e estado definitivo são da API. */
export function acoesParaEstado(estado: EstadoComentario, temDenuncias: boolean): readonly AcaoModeracao[] {
  if (estado === "PENDENTE") return ["APROVAR", "REJEITAR"];
  if (estado === "SUSPENSO") return ["RESTAURAR", "REMOVER"];
  if (estado === "PUBLICADO" && temDenuncias) return ["MANTER", "REMOVER"];
  return [];
}

export function statusModeracao(erro: unknown): number | null {
  return erro instanceof ApiError ? erro.status : null;
}

export function mensagemModeracao(erro: unknown, operacao: "consulta" | "acao"): string {
  switch (statusModeracao(erro)) {
    case 401: return "Sua sessão não está disponível. Entre com uma conta de moderador e retorne à fila.";
    case 403: return operacao === "acao"
      ? "Ação não permitida. Casos de autoria ou denúncia própria devem ser analisados por outro moderador."
      : "Acesso restrito a moderadores autorizados com e-mail confirmado.";
    case 404: return "Este conteúdo não está mais disponível. Atualize a fila.";
    case 409: return "O estado do conteúdo mudou e esta ação não pôde ser aplicada. Confira a fila novamente.";
    case 422: return "Revise a ação selecionada e preencha o motivo da decisão.";
    default: return operacao === "acao"
      ? "Não foi possível confirmar o resultado da ação. Atualize o conteúdo antes de tentar novamente."
      : "Não foi possível carregar a moderação. Verifique sua conexão e tente novamente.";
  }
}
