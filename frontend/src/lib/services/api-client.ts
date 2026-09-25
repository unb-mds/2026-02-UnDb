import { ApiError } from "./http-error";

/**
 * Base da API institucional pública (Issue #25) — sem autenticação, RF04.
 * No navegador, usa a URL pública definida no build. No servidor, permite
 * acessar a API pela rede interna do Compose; ver .env.example.
 */
const PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function apiBaseUrl(): string {
  return typeof window === "undefined"
    ? process.env.API_INTERNAL_URL || PUBLIC_API_URL
    : PUBLIC_API_URL;
}

function buildQuery(params: Record<string, string | undefined>): string {
  const entries = Object.entries(params).filter(
    (entry): entry is [string, string] => entry[1] !== undefined && entry[1] !== "",
  );
  if (entries.length === 0) return "";
  return "?" + new URLSearchParams(entries).toString();
}

async function request<T>(path: string, query: Record<string, string | undefined> = {}): Promise<T> {
  const url = `${apiBaseUrl()}${path}${buildQuery(query)}`;
  const response = await fetch(url, { credentials: "include" });

  if (!response.ok) {
    const detalhe = await response.json().catch(() => null);
    throw new ApiError(mensagemErro(detalhe?.detail), response.status, detalhe?.detail);
  }

  return response.json() as Promise<T>;
}

async function post<TResponse, TBody>(path: string, body: TBody): Promise<TResponse> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detalhe = await response.json().catch(() => null);
    const mensagem = mensagemErro(detalhe?.detail);
    throw new ApiError(mensagem, response.status, detalhe?.detail);
  }

  return response.json() as Promise<TResponse>;
}

export const apiClient = { post, request };

function mensagemErro(detalhe: unknown): string {
  if (typeof detalhe === "string") return detalhe;
  if (Array.isArray(detalhe)) {
    const mensagens = detalhe.flatMap((item) =>
      item && typeof item.msg === "string" ? [item.msg] : [],
    );
    if (mensagens.length) return mensagens.join(" ");
  }
  return "Não foi possível concluir a solicitação.";
}
