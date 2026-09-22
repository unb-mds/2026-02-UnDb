import { apiClient } from "./api-client";

export type CadastroInput = {
  nome: string;
  email: string;
  senha: string;
};

export type LoginInput = {
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

export async function entrar(dados: LoginInput): Promise<MensagemResponse> {
  return apiClient.post<MensagemResponse, LoginInput>("/api/auth/login", dados);
}

export async function sair(): Promise<MensagemResponse> {
  return apiClient.post<MensagemResponse, Record<string, never>>("/api/auth/logout", {});
}
