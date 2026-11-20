export const categorias = {
  DADO_INCORRETO: "Dado institucional incorreto", COMENTARIO_ILICITO: "Comentário potencialmente ilícito",
  NOTA_SUSPEITA: "Nota suspeita", FRAUDE_COORDENADA: "Fraude coordenada",
  EXPOSICAO_PESSOAL: "Exposição pessoal", DIREITO_LGPD: "Direito LGPD", OUTRA: "Outra reclamação fundamentada",
};
export type Evento = { tipo: string; texto: string; data: string; responsavel_id?: string | null };
export type Solicitacao = { protocolo: string; categoria: string; alvo: string; descricao: string; evidencia: string; recebido_em: string; historico: Evento[] };
export type Recibo = { protocolo: string; chave: string; recebido_em: string };
