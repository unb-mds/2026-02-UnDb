import { ApiError } from "./http-error";

/**
 * Base da API institucional pública (Issue #25) — sem autenticação, RF04.
 * Configurar em .env.local; ver .env.example.
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function buildQuery(params: Record<string, string | undefined>): string {
  const entries = Object.entries(params).filter(
    (entry): entry is [string, string] => entry[1] !== undefined && entry[1] !== "",
  );
  if (entries.length === 0) return "";
  return "?" + new URLSearchParams(entries).toString();
}

async function request<T>(path: string, query: Record<string, string | undefined> = {}): Promise<T> {
  const url = `${API_BASE_URL}${path}${buildQuery(query)}`;
  const response = await fetch(url);

  if (!response.ok) {
    const detalhe = await response.json().catch(() => null);
    throw new ApiError(detalhe?.detail ?? `Falha ao consultar ${path}`, response.status);
  }

  return response.json() as Promise<T>;
}

export const apiClient = { request };
