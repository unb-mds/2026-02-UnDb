/** Erro tipado para respostas HTTP da API do G7, para telas distinguirem "não encontrado" de outra falha. */
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly detalhes?: unknown,
    public readonly retryAfter: number | null = null,
  ) {
    super(status === 429 || status === 503 ? mensagemTemporaria(status, retryAfter) : message);
    this.name = "ApiError";
    if (this.temporario) this.detalhes = undefined;
  }

  get temporario(): boolean {
    return this.status === 429 || this.status === 503;
  }

  get naoEncontrado(): boolean {
    return this.status === 404;
  }
}

/** Retry-After admite segundos inteiros ou data HTTP, nunca texto livre na interface. */
export function interpretarRetryAfter(valor: string | null, agora = Date.now()): number | null {
  if (!valor?.trim()) return null;
  const texto = valor.trim();
  if (/^\d+$/.test(texto)) {
    const segundos = Number(texto);
    return Number.isSafeInteger(segundos) ? Math.max(1, segundos) : null;
  }
  if (!/^[A-Za-z]{3}, \d{2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} GMT$/.test(texto)) return null;
  const data = Date.parse(texto);
  return Number.isFinite(data) ? Math.max(1, Math.ceil((data - agora) / 1000)) : null;
}

function mensagemTemporaria(status: number, segundos: number | null): string {
  const inicio = status === 429 ? "Muitas tentativas em pouco tempo." : "Serviço temporariamente indisponível.";
  return segundos === null
    ? `${inicio} Tente novamente em instantes. Seus dados foram mantidos.`
    : `${inicio} Aguarde ${segundos} ${segundos === 1 ? "segundo" : "segundos"} antes de tentar novamente. Seus dados foram mantidos.`;
}

export function mensagemErroTemporario(erro: unknown): string | null {
  return erro instanceof ApiError && erro.temporario ? erro.message : null;
}
