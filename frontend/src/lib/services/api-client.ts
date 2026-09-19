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
  const response = await fetch(url);

  if (!response.ok) {
    const detalhe = await response.json().catch(() => null);
    throw new ApiError(detalhe?.detail ?? `Falha ao consultar ${path}`, response.status);
  }

  return response.json() as Promise<T>;
}

export const apiClient = { request };
