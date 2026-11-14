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
  moderador_id: string | null;
  acao: AcaoModeracao;
  motivo: string;
  estado_anterior: EstadoComentario;
  estado_posterior: EstadoComentario;
  created_at: string;
};
export type AcaoModeracaoInput = { acao: AcaoModeracao; motivo: string };

export const statusTriagem = ["CONCLUIDA", "DESATIVADA", "DADOS_SENSIVEIS", "LIMITE", "INDISPONIVEL"] as const;
export type TriagemComentario = {
  comentario_versao_id: string;
  status: (typeof statusTriagem)[number];
  filtro_ativo: boolean;
  versao_lista: string;
  categorias_locais: MotivoDenuncia[];
  categorias_ia: CategoriaOpenAI[];
  sinalizado: boolean | null;
  modelo: string | null;
  versao_integracao: string;
};

export const categoriasOpenAI = ["harassment", "harassment/threatening", "hate", "hate/threatening", "illicit", "illicit/violent", "self-harm", "self-harm/intent", "self-harm/instructions", "sexual", "sexual/minors", "violence", "violence/graphic"] as const;
export type CategoriaOpenAI = (typeof categoriasOpenAI)[number];
export const rotulosOpenAI: Record<CategoriaOpenAI, string> = {
  harassment: "Assédio ou linguagem hostil", "harassment/threatening": "Assédio com ameaça",
  hate: "Ódio ou discriminação", "hate/threatening": "Ódio com ameaça",
  illicit: "Instruções de atividade ilícita", "illicit/violent": "Instruções de atividade ilícita violenta",
  "self-harm": "Conteúdo de autolesão", "self-harm/intent": "Intenção de autolesão",
  "self-harm/instructions": "Instruções de autolesão", sexual: "Conteúdo sexual",
  "sexual/minors": "Conteúdo sexual envolvendo menores", violence: "Violência", "violence/graphic": "Violência gráfica",
};
