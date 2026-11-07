import { identificadorValido } from "../identificador";
import {
  motivosDenuncia,
  type Agradecimento,
  type ConfirmacaoDenuncia,
  type DenunciaInput,
} from "../types/denuncia";
import { apiClient } from "./api-client";
import { ApiError } from "./http-error";

const registro = (valor: unknown): valor is Record<string, unknown> =>
  typeof valor === "object" && valor !== null && !Array.isArray(valor);

const idValido = (valor: unknown): valor is string =>
  typeof valor === "string" && identificadorValido(valor);

function agradecimento(valor: unknown): valor is Agradecimento {
  return (
    registro(valor) &&
    idValido(valor.id) &&
    typeof valor.mensagem === "string"
  );
}

function confirmacao(valor: unknown): valor is ConfirmacaoDenuncia {
  return registro(valor) && typeof valor.mensagem === "string";
}

function validar<T>(valor: unknown, guarda: (valor: unknown) => valor is T): T {
  if (!guarda(valor)) {
    throw new Error("Resposta de denúncia incompatível com o contrato.");
  }
  return valor;
}

export async function registrarDenuncia(
  versaoId: string,
  dados: DenunciaInput,
  signal?: AbortSignal,
): Promise<ConfirmacaoDenuncia> {
  if (!identificadorValido(versaoId)) {
    throw new Error("Identificador de versão inválido.");
  }
  if (!motivosDenuncia.some((m) => m === dados.motivo)) {
    throw new Error("Motivo de denúncia inválido.");
  }

  const resposta = await apiClient.post<unknown, DenunciaInput>(
    `/api/comentarios/${versaoId}/denuncias`,
    { motivo: dados.motivo },
    { signal },
  );

  return validar(resposta, confirmacao);
}

export async function listarAgradecimentos(
  signal?: AbortSignal,
): Promise<Agradecimento[]> {
  try {
    const resposta = await apiClient.request<unknown>(
      "/api/agradecimentos",
      {},
      { cache: "no-store", signal },
    );
    return validar(
      resposta,
      (valor): valor is Agradecimento[] =>
        Array.isArray(valor) && valor.every(agradecimento),
    );
  } catch (erro) {
    if (erro instanceof ApiError && erro.status === 401) {
      // Visitante ou sem sessão: não recebe acompanhamento posterior
      return [];
    }
    throw erro;
  }
}

export async function confirmarAgradecimentoExibido(
  mensagemId: string,
  signal?: AbortSignal,
): Promise<void> {
  if (!identificadorValido(mensagemId)) {
    throw new Error("Identificador de mensagem inválido.");
  }
  await apiClient.post<void, Record<string, never>>(
    `/api/agradecimentos/${mensagemId}/exibido`,
    {},
    { signal },
  );
}
