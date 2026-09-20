import { apiClient } from "./api-client";

export type CadastroInput = {
  nome: string;
  email: string;
  senha: string;
};

type MensagemResponse = {
  message: string;
};

export async function cadastrarUsuario(dados: CadastroInput): Promise<MensagemResponse> {
  return apiClient.post<MensagemResponse, CadastroInput>("/api/auth/cadastro", dados);
}

export async function confirmarEmail(token: string): Promise<MensagemResponse> {
  return apiClient.post<MensagemResponse, { token: string }>("/api/auth/confirmar", { token });
}
