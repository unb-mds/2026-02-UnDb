import { motivosDenuncia, type MotivoDenuncia } from "./moderacao";

export { motivosDenuncia, type MotivoDenuncia };

export const ROTULOS_MOTIVOS_DENUNCIA: Record<MotivoDenuncia, string> = {
  OFENSA_PESSOAL: "Ofensa pessoal",
  XINGAMENTO: "Xingamento",
  PALAVRAO: "Palavrão",
  AMEACA: "Ameaça",
  DISCRIMINACAO: "Discriminação",
  EXPOSICAO_DADOS_PESSOAIS: "Exposição de dados pessoais",
  SPAM: "Spam",
};

export type DenunciaInput = {
  motivo: MotivoDenuncia;
};

export type ConfirmacaoDenuncia = {
  mensagem: string;
};

export type Agradecimento = {
  id: string;
  mensagem: string;
};
