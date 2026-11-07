import { apiClient } from "./api-client";

export const EVENTO_SESSAO_ALTERADA = "undb:sessao-alterada";

function notificarSessao() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(EVENTO_SESSAO_ALTERADA));
  }
}

export type CadastroInput = {
  nome: string;
  email: string;
  senha: string;
  return_to?: string;
};

export type LoginInput = {
  email: string;
  senha: string;
};

type MensagemResponse = {
  message: string;
};

type SessaoResponse = {
  autenticado: boolean;
};

export async function cadastrarUsuario(dados: CadastroInput): Promise<MensagemResponse> {
  return apiClient.post<MensagemResponse, CadastroInput>("/api/auth/cadastro", dados);
}

export async function confirmarEmail(token: string): Promise<MensagemResponse> {
  return apiClient.post<MensagemResponse, { token: string }>("/api/auth/confirmar", { token });
}

export async function entrar(dados: LoginInput): Promise<MensagemResponse> {
  const resposta = await apiClient.post<MensagemResponse, LoginInput>("/api/auth/login", dados);
  notificarSessao();
  return resposta;
}

export async function consultarSessao(): Promise<SessaoResponse> {
  return apiClient.request<SessaoResponse>("/api/auth/sessao");
}

export async function sair(): Promise<MensagemResponse> {
  const resposta = await apiClient.post<MensagemResponse, Record<string, never>>("/api/auth/logout", {});
  notificarSessao();
  return resposta;
}
