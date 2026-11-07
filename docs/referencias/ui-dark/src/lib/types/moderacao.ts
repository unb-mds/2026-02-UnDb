/** Contrato privado da PR #192. Não usar em consultas públicas de comentários. */
export const estadosComentario = ["PENDENTE", "PUBLICADO", "SUSPENSO", "REMOVIDO", "RETIRADO", "SUBSTITUIDO", "REJEITADO"] as const;
export type EstadoComentario = (typeof estadosComentario)[number];
export type EstadoFila = Extract<EstadoComentario, "PENDENTE" | "PUBLICADO" | "SUSPENSO">;
export const acoesModeracao = ["APROVAR", "REJEITAR", "MANTER", "RESTAURAR", "REMOVER"] as const;
export type AcaoModeracao = (typeof acoesModeracao)[number];
export const motivosDenuncia = ["OFENSA_PESSOAL", "XINGAMENTO", "PALAVRAO", "AMEACA", "DISCRIMINACAO", "EXPOSICAO_DADOS_PESSOAIS", "SPAM"] as const;
export type MotivoDenuncia = (typeof motivosDenuncia)[number];

export type IdentidadeInterna = { id: string; nome: string; email: string };
export type ComentarioModeracao = {
  id: string;
  texto: string | null;
  estado: EstadoComentario;
  autor: IdentidadeInterna;
  substitui_id: string | null;
  created_at: string;
};
export type DenunciaInterna = {
  id: string;
  comentario_versao_id: string;
  motivo: MotivoDenuncia;
  estado: "EM_ABERTO";
  created_at: string;
  denunciante: IdentidadeInterna | null;
};
export type DenunciasDaVersao = {
  autenticadas: DenunciaInterna[];
  visitantes: DenunciaInterna[];
  contas_distintas: number;
  total_visitantes: number;
};
export type DecisaoModeracao = {
  id: string;
  comentario_versao_id: string;
  moderador_id: string;
  acao: AcaoModeracao;
  motivo: string;
  estado_anterior: EstadoComentario;
  estado_posterior: EstadoComentario;
  created_at: string;
};
export type AcaoModeracaoInput = { acao: AcaoModeracao; motivo: string };
